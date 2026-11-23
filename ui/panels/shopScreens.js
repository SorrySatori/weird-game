/**
 * shopScreens.js: the SHOP screen in the two panel sets (ui/panelStyle.js; Settings "Vzhled panelů: Učedník / Úřad",
 * setting 'panelSet'). ShopSystem opens SHOP_SCREENS[panelSet()](scene, ctx) in the paper overlay scene.
 *
 *   apprentice  Stánek: a market stall, the wares on shelves under a striped awning with handwritten price tags, a
 *               little chalk board with the chosen piece's price; the detail on the set's pinned note (right)
 *   office      Katalog: a printed mail-order page (numbered entries, typed prices, a dotted leader), manila folder
 *               tabs; the detail on the set's lined index card as an order form (right)
 * Both: Buy / Sell are the set's tabs (drawTabs), the chosen piece wears the set's mark (markChosen), prices you can't
 * pay are in the set's red.
 *
 * ctx (systems/items/ShopSystem.js screenCtx):
 *   scene, W, H, lang ('cs' | 'en'), t(key, params, fallback), title (the shop's name), shopKey ('zerren' | 'kloor' | 'cork' | null)
 *   tabs: [{ key: 'buy', label }, { key: 'sell', label }], tab() → 'buy' | 'sell', setTab(key)   (then redraw yourself)
 *   items() → the current tab's items, name(it), desc(it), kind(it), qty(it), price(it) → number, canAfford(it)
 *   actLabel() → 'Koupit' / 'Prodat', act(it)  buys / sells it (the owner then calls screen.refresh())
 *   money() → dinar, iconKey(it) → texture key | null, icon(it, x, y, k) → a 60*k px image (or a lettered disc)
 *   empty() → the text for an empty tab, strings: { forSale, yourItems, price(p), balance(a), hint }
 *   sound(key, vol)  'hoverSound' | 'clickSound', close()
 * screen: { refresh(), key(code, event), footer() }  footer() is called every frame while the shop is open (money)
 *
 * shopCore below holds what both share: the state (tab, page, chosen, hovered), the hit boxes, the pointer and the
 * keys. Hover is worked out from the pointer's position over the hit boxes each move (zones re-made on every redraw
 * never send their pointerout; the zones there are only for the hand cursor). Hovering an item previews it, leaving
 * falls back to the chosen one, a click chooses; arrows move the choice, Enter / Space buy or sell it, Tab switches
 * Buy / Sell, PgUp / PgDn or the wheel turn pages. Canvas textures are prefixed 'sh_'. Depths: backdrop 1, the detail
 * paper 2, items 3, detail texts 4, ui 5, the cursor zones 9.
 */
import { tex, rng, fitHeight, SERIF, MONO } from '../paperKit.js';
import { LOOK, detailCard, markChosen, drawTabs } from '../panelStyle.js';

const tr = (ctx, cs, en) => (ctx.lang === 'cs' ? cs : en);

/** cut a one-line text to maxW with an ellipsis */
function ellipsize(t, maxW) {
    let s = t.text;
    while (t.width > maxW && s.length > 2) { s = s.slice(0, -1); t.setText(s.trimEnd() + '…'); }
    return t;
}

function speckle(c, w, h, n, col, seed, a0 = 0.03, a1 = 0.08) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
        c.fillStyle = `rgba(${col},${a0 + r() * (a1 - a0)})`;
        c.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 1.5);
    }
}

function glowTex(scene) {
    return tex(scene, 'sh_glow', 64, 64, (c, w, h) => {
        const g = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
        g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.45, 'rgba(255,255,255,0.4)'); g.addColorStop(1, 'rgba(255,255,255,0)');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    });
}

// ---------------------------------------------------------------------------------------------------------------
// the shared machinery

function shopCore(scene, ctx, d) {
    const st = { page: 0, sel: null, hover: null, hot: null };
    const mk = (z) => scene.add.container(0, 0).setDepth(z);
    const L = { items: mk(3), detail: mk(4), ui: mk(5), zones: mk(9) };
    const hits = [];
    const isBuy = () => ctx.tab() === 'buy';
    const all = () => ctx.items();
    const pages = () => Math.max(1, Math.ceil(all().length / d.pageSize));
    const pageItems = () => all().slice(st.page * d.pageSize, (st.page + 1) * d.pageSize);
    const api = {
        scene, ctx, st, L, isBuy, pages, pageItems, all,
        shown: () => st.hover || st.sel,
        bad: (it) => isBuy() && !ctx.canAfford(it),
        add: (layer, o) => { L[layer].add(o); return o; },
        hit: (kind, x, y, w, h, data = {}) => { hits.push({ kind, x, y, w, h, id: data.id || kind, ...data }); },
        isHot: (id) => st.hot === id,
        money: null                                      // a text the design makes; footer() keeps it current
    };
    const fix = () => {
        const items = all();
        if (st.sel && !items.includes(st.sel)) st.sel = null;
        if (st.hover && !items.includes(st.hover)) st.hover = null;
        st.page = Phaser.Math.Clamp(st.page, 0, pages() - 1);
        if (!st.sel && items.length) st.sel = pageItems()[0] || items[0];
    };
    const footer = () => { if (api.money?.active) api.money.setText(d.moneyText(api, ctx.money())); };
    const redraw = () => {
        fix();
        for (const k of Object.keys(L)) L[k].removeAll(true);
        hits.length = 0;
        api.money = null;
        d.draw(api);
        for (const h of hits) L.zones.add(scene.add.zone(h.x, h.y, h.w, h.h).setInteractive({ useHandCursor: true }));
        footer();
    };
    const setTab = (key) => {
        if (key === ctx.tab()) return;
        ctx.setTab(key);
        st.page = 0; st.sel = null; st.hover = null;
        ctx.sound('clickSound');
        redraw();
    };
    const turn = (p) => {
        p = Phaser.Math.Clamp(p, 0, pages() - 1);
        if (p === st.page) return;
        st.page = p; st.sel = pageItems()[0] || null; st.hover = null;
        ctx.sound('clickSound');
        redraw();
    };
    const act = () => {
        const it = st.sel;
        if (!it) return;
        if (api.bad(it)) scene.cameras.main.shake(140, 0.003);       // (the "not enough dinar" notice is under the panel)
        ctx.sound('clickSound');
        ctx.act(it);
    };
    /** Buy / Sell as the set's tabs (they handle their own clicks) */
    const tabs = (set, x, y) => drawTabs(scene, set, L.ui, x, y, ctx.tabs.map(t => ({ label: t.label })),
        ctx.tabs.findIndex(t => t.key === ctx.tab()), (i) => setTab(ctx.tabs[i].key));
    Object.assign(api, { act, setTab, turn, tabs });
    scene.add.rectangle(0, 0, ctx.W, ctx.H, 0x050403).setOrigin(0).setDepth(0.5);
    d.backdrop(api);

    const at = (p) => {
        for (let i = hits.length - 1; i >= 0; i--) {
            const h = hits[i];
            if (Math.abs(p.x - h.x) <= h.w / 2 && Math.abs(p.y - h.y) <= h.h / 2) return h;
        }
        return null;
    };
    scene.input.on('pointermove', (p) => {
        const h = at(p);
        const hover = h && h.kind === 'item' ? h.it : null, hot = h && h.kind !== 'item' ? h.id : null;
        if (hover !== st.hover || hot !== st.hot) {
            if (hover && hover !== st.hover) ctx.sound('hoverSound', 0.3);
            st.hover = hover; st.hot = hot;
            redraw();
        }
    });
    scene.input.on('pointerdown', (p) => {
        const h = at(p);
        if (!h) return;
        if (h.kind === 'item') { st.sel = h.it; st.hover = h.it; ctx.sound('clickSound'); redraw(); }
        else if (h.kind === 'act') act();
        else if (h.kind === 'page') turn(st.page + h.d);
    });
    scene.input.on('gameout', () => { if (st.hover || st.hot) { st.hover = null; st.hot = null; redraw(); } });
    scene.input.on('wheel', (p, o, dx, dy) => turn(st.page + Math.sign(dy)));
    redraw();

    return {
        refresh: redraw,
        footer,
        shown: api.shown,                          // (tests) what the detail shows
        hits,                                      // (tests) the current hit boxes
        key(code, ev) {
            if (code === 'Tab') {
                ev?.preventDefault?.();
                const i = ctx.tabs.findIndex(t => t.key === ctx.tab());
                setTab(ctx.tabs[(i + 1) % ctx.tabs.length].key);
                return;
            }
            const page = pageItems(), i = page.indexOf(st.sel), cols = d.cols || 4;
            const step = { ArrowRight: 1, KeyD: 1, ArrowLeft: -1, KeyA: -1, ArrowDown: cols, KeyS: cols, ArrowUp: -cols, KeyW: -cols }[code];
            if (step !== undefined && page.length) {
                st.hover = null;
                st.sel = page[Phaser.Math.Clamp(i < 0 ? 0 : i + step, 0, page.length - 1)];
                ctx.sound('hoverSound', 0.35);
                redraw();
            } else if (code === 'PageDown') turn(st.page + 1);
            else if (code === 'PageUp') turn(st.page - 1);
            else if (code === 'Enter' || code === 'NumpadEnter' || code === 'Space') act();
        }
    };
}

// ---------------------------------------------------------------------------------------------------------------
// apprentice: Stánek, a market stall

function buildStall(scene, ctx) {
    const { W, H } = ctx;
    const LK = LOOK.apprentice, T = LK.text, D = LK.DETAIL;
    const SHELF = [170, 295, 420];
    const slotX = (col) => 102 + col * 156;
    const BOARD = { x: 668, y: 78, w: 108, h: 176 };       // the chalk price board on the stall's post
    let card;
    return shopCore(scene, ctx, {
        pageSize: 12, cols: 4,
        moneyText: (api, m) => ctx.strings.balance(m),
        backdrop() {
            scene.add.image(0, 0, tex(scene, 'sh_stall_bg2', W, H, (c) => {
                const g = c.createLinearGradient(0, 0, 0, H);
                g.addColorStop(0, '#1d1814'); g.addColorStop(1, '#0c0907');
                c.fillStyle = g; c.fillRect(0, 0, W, H);
                // the back wall of planks
                for (let y = 44, i = 0; y < 470; y += 22, i++) {
                    c.fillStyle = i % 2 ? '#4e331f' : '#56381f'; c.fillRect(24, y, 632, 22);
                    c.fillStyle = 'rgba(0,0,0,0.35)'; c.fillRect(24, y + 21, 632, 1);
                }
                c.save(); c.translate(24, 44); speckle(c, 632, 426, 5000, '0,0,0', 3, 0.04, 0.12); speckle(c, 632, 426, 1500, '255,220,170', 4, 0.02, 0.05); c.restore();
                // posts (the right one carries the chalk board)
                for (const x of [14, 652]) {
                    c.fillStyle = '#3a2414'; c.fillRect(x, 30, 18, 440);
                    c.fillStyle = 'rgba(255,220,170,0.12)'; c.fillRect(x + 2, 30, 3, 440);
                }
                // the shelves and their brackets
                for (const y of SHELF) {
                    const sg = c.createLinearGradient(0, y + 12, 0, y + 26);
                    sg.addColorStop(0, 'rgba(0,0,0,0.5)'); sg.addColorStop(1, 'rgba(0,0,0,0)');
                    c.fillStyle = sg; c.fillRect(32, y + 12, 620, 14);
                    c.fillStyle = '#8a5c34'; c.fillRect(32, y, 620, 12);
                    c.fillStyle = '#b07a48'; c.fillRect(32, y, 620, 2);
                    c.fillStyle = '#3a2414';
                    for (const x of [48, 340, 624]) { c.beginPath(); c.moveTo(x, y + 12); c.lineTo(x + 14, y + 12); c.lineTo(x + 2, y + 30); c.closePath(); c.fill(); }
                }
                // the striped awning, scalloped
                for (let x = 8, i = 0; x < 672; x += 42, i++) {
                    c.fillStyle = i % 2 ? '#d9c9a6' : '#7a2a24';
                    c.fillRect(x, 0, 42, 40);
                    c.beginPath(); c.arc(x + 21, 40, 21, 0, Math.PI); c.fill();
                }
                c.fillStyle = 'rgba(0,0,0,0.25)'; c.fillRect(8, 0, 664, 6);
                // the chalk price board, hung from the post by a string
                c.strokeStyle = 'rgba(216,200,160,0.8)'; c.lineWidth = 1.5;
                c.beginPath(); c.moveTo(660, 60); c.lineTo(BOARD.x + 20, BOARD.y); c.moveTo(660, 60); c.lineTo(BOARD.x + BOARD.w - 20, BOARD.y); c.stroke();
                c.fillStyle = '#6b4626'; c.fillRect(BOARD.x, BOARD.y, BOARD.w, BOARD.h);
                c.fillStyle = '#1e2622'; c.fillRect(BOARD.x + 8, BOARD.y + 8, BOARD.w - 16, BOARD.h - 16);
                c.save(); c.translate(BOARD.x + 8, BOARD.y + 8); speckle(c, BOARD.w - 16, BOARD.h - 16, 900, '255,255,255', 7, 0.015, 0.05);
                c.strokeStyle = 'rgba(255,255,255,0.05)'; c.lineWidth = 14; c.beginPath(); c.arc(46, 90, 50, 0.4, 2.2); c.stroke();
                c.restore();
                // the counter
                c.fillStyle = '#5a3a22'; c.fillRect(0, 482, W, H - 482);
                for (let x = 0; x < W; x += 64) { c.fillStyle = 'rgba(0,0,0,0.3)'; c.fillRect(x, 482, 2, H - 482); }
                c.save(); c.translate(0, 482); speckle(c, W, H - 482, 4000, '0,0,0', 8, 0.04, 0.12); c.restore();
                c.fillStyle = '#9a6a3c'; c.fillRect(0, 466, W, 16);
                c.fillStyle = '#c08a54'; c.fillRect(0, 466, W, 2);
                c.fillStyle = 'rgba(0,0,0,0.45)'; c.fillRect(0, 482, W, 5);
            })).setOrigin(0).setDepth(1);
            card = detailCard(scene, 'apprentice');
        },
        draw(api) {
            const { st } = api;
            const page = api.pageItems();
            if (!page.length) api.add('items', scene.add.text(340, 250, ctx.empty(), { ...T.hand, fontSize: '26px', color: '#e8d6b6', align: 'center', wordWrap: { width: 480 } }).setOrigin(0.5));
            page.forEach((it, k) => {
                const col = k % 4, row = Math.floor(k / 4), x = slotX(col), sy = SHELF[row];
                const up = it === api.shown(), sel = it === st.sel;
                if (up) api.add('items', scene.add.image(x, sy - 32, glowTex(scene)).setTint(0xffd9a0).setBlendMode(Phaser.BlendModes.ADD).setDisplaySize(130, 100).setAlpha(sel ? 0.32 : 0.22));
                api.add('items', scene.add.ellipse(x, sy - 1, 54, 8, 0x000000, 0.35));
                api.add('items', ctx.icon(it, x, sy - 31 - (up ? 4 : 0), 1));
                if (ctx.qty(it) > 1) api.add('items', scene.add.text(x + 34, sy - 8, `×${ctx.qty(it)}`, { ...T.label, color: '#f3e2c4', stroke: '#2a120c', strokeThickness: 3 }).setOrigin(0, 1));
                if (sel) api.add('items', markChosen(scene, 'apprentice', x, sy - 34, 96, 80));
                // the handwritten price tag on a string under the shelf
                const bad = api.bad(it), tx = x + 22;
                api.add('items', scene.add.line(0, 0, tx, sy + 12, tx, sy + 22, 0xd8c8a0).setOrigin(0));
                const pt = scene.add.text(tx, sy + 32, `${ctx.price(it)}`, { ...T.label, fontSize: '19px', color: bad ? '#fff0e6' : LK.INK }).setOrigin(0.5).setRotation(0.06);
                api.add('items', scene.add.rectangle(tx, sy + 32, Math.max(36, pt.width + 14), 21, bad ? LK.MARK : 0xe6d6b0).setStrokeStyle(1, 0x6a5030).setRotation(0.06));
                api.add('items', scene.add.circle(tx, sy + 24, 1.8, 0x3a2a1a));
                api.add('items', pt);
                api.hit('item', x, sy - 40, 148, 104, { it });
            });

            // Buy / Sell: sticky notes on the counter front
            api.tabs('apprentice', 36, 532);
            if (api.pages() > 1) {
                const y = 532;
                [[-1, 318, '‹'], [1, 430, '›']].forEach(([dd, x, s]) => {
                    const ok = st.page + dd >= 0 && st.page + dd < api.pages();
                    api.add('ui', scene.add.text(x, y, s, { fontFamily: SERIF, fontSize: '34px', color: ok ? (api.isHot('page' + dd) ? '#ffffff' : '#f0dfb8') : '#6a5040' }).setOrigin(0.5));
                    if (ok) api.hit('page', x, y, 40, 46, { d: dd, id: 'page' + dd });
                });
                api.add('ui', scene.add.text(374, y, `${st.page + 1}/${api.pages()}`, { ...T.hand, color: '#f0dfb8' }).setOrigin(0.5));
            }

            // the chalk price board
            const it = api.shown(), bcx = BOARD.x + BOARD.w / 2;
            const chalk = (y, s, style) => api.add('detail', scene.add.text(bcx, y, s, { fontFamily: 'Caveat', fontSize: '20px', color: '#e8eee6', ...style }).setOrigin(0.5));
            chalk(BOARD.y + 26, tr(ctx, api.isBuy() ? 'cena' : 'dáme ti', api.isBuy() ? 'price' : 'we pay'), { color: '#cfd8cf' });
            if (it) {
                const bad = api.bad(it);
                chalk(BOARD.y + 82, `${ctx.price(it)}`, { fontStyle: 'bold', fontSize: '48px', color: bad ? '#ff9a86' : '#f2e3a0' });
                chalk(BOARD.y + 126, tr(ctx, 'dinárů', 'dinar'), { color: '#cfd8cf' });
                if (bad) chalk(BOARD.y + 150, tr(ctx, 'to nemáš', 'too dear'), { fontSize: '17px', color: '#ff9a86' });
            } else chalk(BOARD.y + 84, '?', { fontSize: '44px' });

            // the note (the set's detail paper)
            const b = card.body, PW = card.w, PH = card.h;
            b.removeAll(true);
            api.money = scene.add.text(18, PH - 26, '', T.small).setOrigin(0, 0.5);
            b.add(api.money);
            if (!it) { b.add(scene.add.text(PW / 2, PH / 2 - 40, page.length ? ctx.strings.hint : ctx.empty(), { ...T.hand, align: 'center', wordWrap: { width: PW - 44 } }).setOrigin(0.5)); return; }
            const nm = scene.add.text(18, 22, ctx.name(it), { ...T.title, wordWrap: { width: PW - 36 } });
            b.add(nm);
            fitHeight(nm, 76, 18);
            let y = nm.y + nm.height + 2;
            b.add(scene.add.graphics().lineStyle(1.5, LK.MARK, 0.7).lineBetween(18, y + 2, PW - 30, y));
            y += 6;
            if (ctx.kind(it)) { const k = scene.add.text(18, y, ctx.kind(it), T.kind); b.add(k); y += k.height + 2; }
            const bad = api.bad(it);
            const pr = scene.add.text(18, y + 2, ctx.strings.price(ctx.price(it)), { ...T.hand, fontStyle: 'bold', color: bad ? LK.MARK_CSS : LK.INK });
            b.add(pr);
            y += pr.height + 4;
            const dsc = scene.add.text(18, y + 4, ctx.desc(it), { ...T.body, wordWrap: { width: PW - 36 } });
            b.add(dsc);
            fitHeight(dsc, PH - 116 - (y + 4), 10);
            // the act slip
            const hot = api.isHot('act'), bx = PW / 2, by = PH - 76;
            b.add(scene.add.rectangle(bx, by, 156, 36, bad ? 0x6a5a4a : hot ? 0xa8322a : 0x8a1f1a, 0.92));
            b.add(scene.add.text(bx, by, ctx.actLabel(), T.button).setOrigin(0.5));
            api.hit('act', D.x + PW / 2 + 2, D.y + by, 156, 36);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------
// office: Katalog, a mail-order page

function buildCatalogue(scene, ctx) {
    const { W, H } = ctx;
    const LK = LOOK.office, T = LK.text, D = LK.DETAIL;
    const PG = { x: 28, y: 30, w: 678, h: 552 };
    const GRID = { x: 44, y: 128, cw: 215, ch: 136 };
    let card;
    return shopCore(scene, ctx, {
        pageSize: 9, cols: 3,
        moneyText: (api, m) => `${m} din.`,
        backdrop() {
            scene.add.image(0, 0, tex(scene, 'sh_cat_bg2', W, H, (c) => {
                c.fillStyle = '#17120e'; c.fillRect(0, 0, W, H);
                const r = rng(31);
                for (let i = 0; i < 120; i++) {
                    c.strokeStyle = `rgba(0,0,0,${0.15 + r() * 0.2})`; c.lineWidth = 0.6 + r() * 1.4;
                    const y = r() * H; c.beginPath(); c.moveTo(0, y);
                    for (let x = 0; x <= W; x += 60) c.lineTo(x, y + Math.sin(x / 80 + i) * 3);
                    c.stroke();
                }
                c.save(); c.filter = 'blur(8px)'; c.fillStyle = 'rgba(0,0,0,0.7)'; c.fillRect(PG.x + 6, PG.y + 10, PG.w, PG.h); c.restore();
                c.fillStyle = '#efe6cf'; c.fillRect(PG.x, PG.y, PG.w, PG.h);
                c.save(); c.translate(PG.x, PG.y); speckle(c, PG.w, PG.h, 9000, '110,85,40', 32);
                const yg = c.createLinearGradient(0, 0, PG.w, 0); yg.addColorStop(0, 'rgba(120,90,30,0.10)'); yg.addColorStop(0.08, 'rgba(120,90,30,0)'); c.fillStyle = yg; c.fillRect(0, 0, PG.w, PG.h);
                c.restore();
                c.fillStyle = '#2a1d10'; c.fillRect(PG.x + 20, PG.y + 70, PG.w - 40, 2.5); c.fillRect(PG.x + 20, PG.y + 76, PG.w - 40, 1);
                c.strokeStyle = 'rgba(60,40,20,0.35)'; c.lineWidth = 1;
                for (let i = 1; i < 3; i++) { const x = GRID.x + i * GRID.cw; c.beginPath(); c.moveTo(x, GRID.y + 6); c.lineTo(x, GRID.y + 3 * GRID.ch - 6); c.stroke(); }
                for (let j = 1; j < 3; j++) { const y = GRID.y + j * GRID.ch; c.beginPath(); c.moveTo(GRID.x + 6, y); c.lineTo(GRID.x + 3 * GRID.cw - 6, y); c.stroke(); }
                c.fillStyle = '#2a1d10'; c.fillRect(PG.x + 20, PG.y + PG.h - 40, PG.w - 40, 1);
            })).setOrigin(0).setDepth(1);
            card = detailCard(scene, 'office');
        },
        draw(api) {
            const { st } = api;
            const all = api.all();
            // the masthead
            const mast = api.add('ui', scene.add.text(PG.x + PG.w / 2, PG.y + 38, ctx.title.toUpperCase(), { fontFamily: SERIF, fontStyle: 'bold', fontSize: '30px', color: LK.INK, letterSpacing: 2 }).setOrigin(0.5));
            ellipsize(mast, PG.w - 60);
            api.add('ui', scene.add.text(PG.x + PG.w / 2, PG.y + 88, `${(api.isBuy() ? ctx.strings.forSale : ctx.strings.yourItems)} · ${tr(ctx, 'ceny v dinárech', 'prices in dinar')}`, { fontFamily: SERIF, fontStyle: 'italic', fontSize: '13px', color: LK.INK_SOFT }).setOrigin(0.5));
            // Buy / Sell: manila folder tabs on the page's top edge
            api.tabs('office', PG.x + 26, PG.y - 10);
            const page = api.pageItems();
            if (!page.length) api.add('items', scene.add.text(PG.x + PG.w / 2, 330, ctx.empty(), { fontFamily: SERIF, fontStyle: 'italic', fontSize: '17px', color: LK.INK_SOFT }).setOrigin(0.5));
            page.forEach((it, k) => {
                const col = k % 3, row = Math.floor(k / 3);
                const x0 = GRID.x + col * GRID.cw, y0 = GRID.y + row * GRID.ch, cx = x0 + GRID.cw / 2, cy = y0 + GRID.ch / 2;
                const sel = it === st.sel, hov = it === st.hover, bad = api.bad(it);
                if (hov) api.add('items', scene.add.rectangle(cx, cy, GRID.cw - 12, GRID.ch - 12, 0xfff06a, 0.28));
                api.add('items', scene.add.text(x0 + 12, y0 + 10, `${tr(ctx, 'Č.', 'No.')} ${String(all.indexOf(it) + 1 + 40).padStart(3, '0')}`, { fontFamily: MONO, fontSize: '10px', color: LK.MARK_CSS }));
                api.add('items', scene.add.rectangle(x0 + 44, y0 + 70, 66, 66).setStrokeStyle(1, 0x5a4630, 0.6));
                api.add('items', ctx.icon(it, x0 + 44, y0 + 70, 1));
                const nm = api.add('items', scene.add.text(x0 + 86, y0 + 28, ctx.name(it), { fontFamily: SERIF, fontStyle: 'bold', fontSize: '13px', color: LK.INK, wordWrap: { width: GRID.cw - 96 } }));
                fitHeight(nm, 50, 10);
                const kind = [ctx.kind(it), ctx.qty(it) > 1 ? `×${ctx.qty(it)}` : ''].filter(Boolean).join(' · ');
                if (kind) ellipsize(api.add('items', scene.add.text(x0 + 86, nm.y + nm.height + 2, kind, { fontFamily: SERIF, fontStyle: 'italic', fontSize: '11px', color: '#6a5a45' })), GRID.cw - 96);
                // the typed price with a dotted leader
                const py = y0 + GRID.ch - 22;
                const pt = api.add('items', scene.add.text(x0 + GRID.cw - 12, py, `${ctx.price(it)} din.`, { fontFamily: MONO, fontSize: '13px', color: bad ? LK.MARK_CSS : LK.INK }).setOrigin(1, 0.5));
                const lead = api.add('items', scene.add.graphics());
                lead.fillStyle(0x5a4630, 0.7);
                for (let x = x0 + 86; x < pt.x - pt.width - 6; x += 5) lead.fillRect(x, py + 5, 1.5, 1.5);
                if (bad) api.add('items', scene.add.line(0, 0, pt.x - pt.width - 2, py + 1, pt.x + 2, py - 1, LK.MARK).setOrigin(0).setLineWidth(1.5));
                if (sel) api.add('items', markChosen(scene, 'office', cx, cy, GRID.cw - 14, GRID.ch - 14));
                api.hit('item', cx, cy, GRID.cw - 4, GRID.ch - 4, { it });
            });
            // the pager at the page's foot
            const fy = PG.y + PG.h - 22;
            api.add('ui', scene.add.text(PG.x + PG.w / 2, fy, tr(ctx, `strana ${st.page + 1} z ${api.pages()}`, `page ${st.page + 1} of ${api.pages()}`), { fontFamily: SERIF, fontStyle: 'italic', fontSize: '13px', color: LK.INK_SOFT }).setOrigin(0.5));
            if (api.pages() > 1) {
                [[-1, PG.x + PG.w / 2 - 80, '‹'], [1, PG.x + PG.w / 2 + 80, '›']].forEach(([dd, x, s]) => {
                    const ok = st.page + dd >= 0 && st.page + dd < api.pages();
                    api.add('ui', scene.add.text(x, fy - 2, s, { fontFamily: SERIF, fontSize: '26px', color: ok ? (api.isHot('page' + dd) ? LK.MARK_CSS : LK.INK) : '#b8a888' }).setOrigin(0.5));
                    if (ok) api.hit('page', x, fy, 36, 34, { d: dd, id: 'page' + dd });
                });
            }

            // the index card as an order form (the set's detail paper)
            const b = card.body, PW = card.w, PH = card.h;
            b.removeAll(true);
            b.add(scene.add.text(62, 18, api.isBuy() ? tr(ctx, 'OBJEDNÁVKA', 'ORDER FORM') : tr(ctx, 'VÝKUPNÍ LÍSTEK', 'SALE SLIP'), T.small).setOrigin(0, 0));   // (right of the clip)
            b.add(scene.add.text(PW - 18, 18, tr(ctx, 'Formulář Z-12', 'Form Z-12'), T.small).setOrigin(1, 0));
            b.add(scene.add.text(18, PH - 64, tr(ctx, 'V HOTOVOSTI', 'CASH IN HAND'), T.small));
            api.money = scene.add.text(PW - 18, PH - 64, '', { fontFamily: MONO, fontSize: '13px', color: LK.LATER }).setOrigin(1, 0);
            b.add(api.money);
            const it = api.shown();
            if (!it) { b.add(scene.add.text(PW / 2, PH / 2 - 30, all.length ? ctx.strings.hint : ctx.empty(), { ...T.body, fontStyle: 'italic', align: 'center', wordWrap: { width: PW - 50 } }).setOrigin(0.5)); return; }
            b.add(scene.add.rectangle(PW / 2, 128, 136, 136).setStrokeStyle(1, 0x5a4a3a, 0.5));
            b.add(ctx.icon(it, PW / 2, 128, 2));
            const nm = scene.add.text(PW / 2, 206, ctx.name(it), { ...T.title, align: 'center', wordWrap: { width: PW - 40 } }).setOrigin(0.5, 0);
            b.add(nm);
            fitHeight(nm, 48, 13);
            let y = nm.y + nm.height + 4;
            if (ctx.kind(it)) { const k = scene.add.text(PW / 2, y, ctx.kind(it).toUpperCase(), T.kind).setOrigin(0.5, 0); b.add(k); y += k.height + 8; }
            const dsc = scene.add.text(18, y + 2, ctx.desc(it), { ...T.body, wordWrap: { width: PW - 36 } });
            b.add(dsc);
            fitHeight(dsc, PH - 136 - (y + 2), 10);
            const bad = api.bad(it);
            b.add(scene.add.text(18, PH - 88, tr(ctx, 'CENA', 'PRICE'), T.small));
            b.add(scene.add.text(PW - 18, PH - 88, `${ctx.price(it)} din.`, { fontFamily: MONO, fontSize: '13px', color: bad ? LK.MARK_CSS : LK.INK }).setOrigin(1, 0));
            // the stamp to press
            const hot = api.isHot('act'), bx = PW / 2, by = PH - 30;
            b.add(scene.add.rectangle(bx, by, 190, 32).setStrokeStyle(2.5, bad ? 0x9a8a80 : LK.MARK).setFillStyle(LK.MARK, hot ? 0.14 : 0));
            b.add(scene.add.text(bx, by, ctx.actLabel().toUpperCase(), { ...T.button, fontSize: '15px', letterSpacing: 4, color: bad ? '#9a8a80' : LK.MARK_CSS }).setOrigin(0.5));
            api.hit('act', D.x + PW / 2 - 2, D.y + by, 190, 32);
        }
    });
}

/** the shop in each panel set (ui/panelStyle.js) */
export const SHOP_SCREENS = { apprentice: buildStall, office: buildCatalogue };
