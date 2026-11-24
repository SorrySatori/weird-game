/**
 * menuDesigns.js — TRIAL: six completely different main-menu designs (title + menu) over Marti's painting, to choose
 * from (MainScene: L cycles them, the choice is remembered). None of them reuses the mechano-fungal kit; each has its
 * own type, colours and layout, and draws its pieces (paper, tape, a rubber stamp, stained glass...) on canvases.
 *
 *   paper    Ateliér       cream paper slips pinned with pink tape (the tape on the photo of the painting), ink + red pencil
 *   cabaret  Kabaret       a crimson theatre ribbon with ivory display type; the menu as a footlight bar along the bottom
 *   glow     Bioluminiscence  neon cyan and magenta light on deep indigo, no panels, glowing type only
 *   slab     Brutal        a black slab hanging from the top, huge white condensed type, acid-yellow tags
 *   office   Úřad          the city's paperwork: a form card, a red rubber stamp, typewriter rows with tick boxes
 *   glass    Vitráž        stained glass after the Egg Cathedral: lead lines, violet/amber/teal/rose glass, blackletter
 *   bandRight / bandLeft / bandBottom
 *            Brutal in a band: the painting is shown WHOLE (side: full height, 848 px wide; bottom: smaller, with a
 *            title column) and the menu lives in a black band beside / under it
 *
 * Each design names its painting layout (paintingLayout: 'full' = the band from the spire to the feet across the
 * screen as before, 'right' / 'left' / 'bottom' = the whole painting beside a band); MainScene places the painting
 * and its life by it.
 *
 * Fonts (assets/fonts/trial, OFL / Apache, licences next to them): Permanent Marker and UnifrakturMaguntia have no
 * Czech carons, so they only set the title (UPPER MORKEZELA); every menu label uses a font with full Czech.
 */
import { playMenuSound } from '../utils/menuKit.js';

const FONT_DIR = 'assets/fonts/trial/';
const FONTS = [
    ['Caveat', 'Caveat.ttf', { weight: '400 700' }],
    ['Permanent Marker', 'PermanentMarker.ttf'],
    ['Abril Fatface', 'AbrilFatface.ttf'],
    ['Cormorant Garamond', 'CormorantGaramond.ttf', { weight: '300 700' }],
    ['Cormorant Garamond Italic', 'CormorantGaramond-Italic.ttf', { weight: '300 700', style: 'italic' }],
    ['Monoton', 'Monoton.ttf'],
    ['Comfortaa', 'Comfortaa.ttf', { weight: '300 700' }],
    ['Bebas Neue', 'BebasNeue.ttf'],
    ['Space Grotesk', 'SpaceGrotesk.ttf', { weight: '300 700' }],
    ['Black Ops One', 'BlackOpsOne.ttf'],
    ['Courier Prime', 'CourierPrime.ttf'],
    ['Courier Prime Bold', 'CourierPrime-Bold.ttf'],
    ['UnifrakturMaguntia', 'UnifrakturMaguntia.ttf'],
    ['Cinzel', 'Cinzel.ttf', { weight: '400 900' }]
];

export function preloadMenuDesigns(scene) {
    for (const [family, file, desc] of FONTS) scene.load.font(family, FONT_DIR + file, 'truetype', desc);
}

// ---------------------------------------------------------------------------------------------------------------
// shared bits

/** a small seeded random, so the torn edges and the glass come out the same every time */
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

/** a canvas texture drawn once (draw(ctx, w, h)); returns its key */
function canvasTex(scene, key, w, h, draw) {
    if (!scene.textures.exists(key)) {
        const tex = scene.textures.createCanvas(key, w, h);
        draw(tex.getContext(), w, h);
        tex.refresh();
        tex.setFilter(Phaser.Textures.FilterMode.LINEAR);
    }
    return key;
}

/** text with the defaults every design wants (crisp, no stroke unless asked) */
function txt(scene, ctx, x, y, s, style) {
    return ctx.add(scene.add.text(x, y, s, { padding: { x: 6, y: 4 }, ...style }).setOrigin(0.5).setDepth(2));
}

/**
 * One menu entry: a container at x, y (w x h hit area) the design fills in build(c); focus(on), press() and
 * enable(on) change its look. Hover and the keys share the focus (MenuNav); ←/→ move too (for a row).
 */
function entry(scene, ctx, i, x, y, w, h, { build, focus, press, enable }) {
    const item = ctx.items[i];
    const c = ctx.add(scene.add.container(x, y).setDepth(2));
    build(c);
    c.setSize(w, h).setInteractive({ useHandCursor: true });
    const handle = {
        container: c, enabled: true, focused: false, busy: false,
        setFocus(on) {
            if ((on && !handle.enabled) || handle.focused === on) return;
            handle.focused = on;
            focus(on);
        },
        activate() {
            if (!handle.enabled || handle.busy) return;
            handle.busy = true;
            playMenuSound(scene, 'clickSound');
            press?.();
            scene.time.delayedCall(140, () => {
                handle.busy = false;
                if (c.active) item.action();
            });
        },
        adjust(d) { ctx.nav.move(d); },
        setEnabled(on) {
            handle.enabled = on;
            enable?.(on);
            if (c.input) c.input.cursor = on ? 'pointer' : 'default';
        }
    };
    c.on('pointerover', () => {
        if (!handle.enabled) return;
        ctx.nav.focus(handle);
        playMenuSound(scene, 'hoverSound', 0.6);
    });
    c.on('pointerout', () => handle.setFocus(false));
    c.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); handle.activate(); });
    ctx.nav.add(handle);
    handle.setEnabled(item.enabled !== false);
    return handle;
}

const tween = (scene, targets, props) => scene.tweens.add({ targets, duration: 160, ease: 'Sine.easeOut', ...props });

// ---------------------------------------------------------------------------------------------------------------
// 1. Ateliér: paper and pink tape

const PAPER = '#efe6d2', INK = '#1d1a17', PENCIL = '#b3322a';

function tornPaper(ctx, w, h, seed, { shadow = true, fill = PAPER } = {}) {
    const r = rng(seed), m = 14;
    const pts = [];
    const edge = (x0, y0, x1, y1, n, amp) => {
        for (let k = 0; k < n; k++) {
            const t = k / n;
            pts.push([x0 + (x1 - x0) * t + (r() - 0.5) * amp * (y0 === y1 ? 0.4 : 1),
                y0 + (y1 - y0) * t + (r() - 0.5) * amp * (x0 === x1 ? 0.4 : 1)]);
        }
    };
    edge(m, m, w - m, m, Math.round(w / 7), 4);
    edge(w - m, m, w - m, h - m, Math.round(h / 7), 4);
    edge(w - m, h - m, m, h - m, Math.round(w / 7), 4);
    edge(m, h - m, m, m, Math.round(h / 7), 4);
    const path = () => { ctx.beginPath(); pts.forEach(([x, y], k) => (k ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); };
    if (shadow) {
        ctx.save(); ctx.filter = 'blur(5px)'; ctx.translate(3, 6); path(); ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fill(); ctx.restore();
    }
    path(); ctx.fillStyle = fill; ctx.fill();
    ctx.save(); path(); ctx.clip();
    for (let k = 0; k < w * h / 40; k++) {          // grain and fibres
        ctx.fillStyle = `rgba(110,90,60,${0.03 + r() * 0.05})`;
        ctx.fillRect(r() * w, r() * h, 1 + r() * 2, 1);
    }
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, 'rgba(255,255,255,0.15)'); g.addColorStop(1, 'rgba(90,70,40,0.12)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
    ctx.restore();
    path(); ctx.strokeStyle = 'rgba(90,70,40,0.25)'; ctx.lineWidth = 1; ctx.stroke();
}

function tape(ctx, w, h, seed) {
    const r = rng(seed);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    for (let y = 0; y <= h; y += 4) ctx.lineTo((y / 4) % 2 ? 3 : 0, y);          // torn short ends
    for (let y = h; y >= 0; y -= 4) ctx.lineTo(w - ((y / 4) % 2 ? 3 : 0), y);
    ctx.closePath();
    ctx.fillStyle = 'rgba(239,127,160,0.82)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.25)';
    for (let k = 0; k < 5; k++) { ctx.beginPath(); const y = r() * h; ctx.moveTo(4, y); ctx.lineTo(w - 4, y + (r() - 0.5) * 3); ctx.stroke(); }
}

function buildPaper(scene, ctx) {
    const { CX } = ctx;
    // the title: a torn strip, two bits of tape
    const title = ctx.add(scene.add.container(CX, 100).setDepth(2).setRotation(-0.025));
    title.add(scene.add.image(0, 0, canvasTex(scene, 'mdPaperTitle', 640, 176, (c, w, h) => tornPaper(c, w, h, 7))));
    const tk = canvasTex(scene, 'mdTape', 92, 30, (c, w, h) => tape(c, w, h, 3));
    title.add(scene.add.image(-292, -62, tk).setRotation(-0.6));
    title.add(scene.add.image(292, -62, tk).setRotation(0.6));
    title.add(scene.add.text(-150, -50, 'Upper', { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '38px', color: INK }).setOrigin(0.5));
    title.add(scene.add.text(0, 4, 'MORKEZELA', { fontFamily: 'Permanent Marker', fontSize: '66px', color: INK, padding: { x: 8, y: 6 } }).setOrigin(0.5));
    title.add(scene.add.text(150, 56, ctx.subtitle, { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '28px', color: PENCIL }).setOrigin(0.5).setRotation(0.03));
    ctx.loop({ targets: title, rotation: -0.015, duration: 4200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

    // the menu: slips, each a little crooked, a bit of tape on the left
    const tilt = [-0.035, 0.028, -0.022, 0.03];
    ctx.items.forEach((item, i) => {
        const rot = tilt[i % 4];
        let slip, label, line;
        entry(scene, ctx, i, CX + (i % 2 ? 10 : -6), 272 + i * 64, 300, 54, {
            build: (c) => {
                c.setRotation(rot);
                slip = scene.add.image(0, 0, canvasTex(scene, 'mdPaperSlip' + i, 316, 74, (cx, w, h) => tornPaper(cx, w, h, 20 + i)));
                label = scene.add.text(0, -2, item.label, { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '34px', color: INK, padding: { x: 6, y: 4 } }).setOrigin(0.5);
                line = scene.add.image(0, 16, canvasTex(scene, 'mdPencilLine', 200, 12, (cx, w, h) => {
                    cx.strokeStyle = PENCIL; cx.lineWidth = 3; cx.lineCap = 'round'; cx.beginPath();
                    for (let x = 4; x <= w - 4; x += 4) cx.lineTo(x, h / 2 + Math.sin(x / 9) * 2.2);
                    cx.stroke();
                })).setAlpha(0);
                c.add([slip, scene.add.image(-142, -14, tk).setScale(0.55).setRotation(-0.9), label, line]);
            },
            focus: (on) => {
                const c = label.parentContainer;
                tween(scene, c, { rotation: on ? 0 : rot, scale: on ? 1.06 : 1 });
                tween(scene, line, { alpha: on ? 1 : 0 });
            },
            press: () => tween(scene, label.parentContainer, { scale: 0.97, yoyo: true, duration: 70 }),
            enable: (on) => { label.setColor(on ? INK : '#8b8477'); slip.setAlpha(on ? 1 : 0.75); }
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------
// 2. Kabaret: a crimson ribbon and a footlight bar

const CRIMSON = '#7a1022', CRIMSON_D = '#4e0913', IVORY = '#f3e6c8', GOLD = '#d4ad55';

function ribbon(ctx, w, h, notch) {
    ctx.save();
    ctx.filter = 'blur(6px)'; ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.beginPath(); ctx.moveTo(10, 12); ctx.lineTo(w - 10, 12); ctx.lineTo(w - 10 - notch, h / 2 + 6); ctx.lineTo(w - 10, h - 2);
    ctx.lineTo(10, h - 2); ctx.lineTo(10 + notch, h / 2 + 6); ctx.closePath(); ctx.fill(); ctx.restore();
    const shape = () => {
        ctx.beginPath(); ctx.moveTo(6, 6); ctx.lineTo(w - 6, 6); ctx.lineTo(w - 6 - notch, h / 2); ctx.lineTo(w - 6, h - 8);
        ctx.lineTo(6, h - 8); ctx.lineTo(6 + notch, h / 2); ctx.closePath();
    };
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, '#951a2e'); g.addColorStop(0.5, CRIMSON); g.addColorStop(1, CRIMSON_D);
    shape(); ctx.fillStyle = g; ctx.fill();
    ctx.save(); shape(); ctx.clip();
    for (let x = 0; x < w; x += 3) { ctx.fillStyle = `rgba(0,0,0,${x % 6 ? 0.05 : 0.1})`; ctx.fillRect(x, 0, 1, h); }    // velvet nap
    ctx.restore();
    ctx.strokeStyle = GOLD; ctx.lineWidth = 2;
    for (const y of [14, 19, h - 22, h - 17]) { ctx.beginPath(); ctx.moveTo(18 + notch, y); ctx.lineTo(w - 18 - notch, y); ctx.stroke(); }
}

function buildCabaret(scene, ctx) {
    const { CX } = ctx;
    ctx.add(scene.add.image(CX, 104, canvasTex(scene, 'mdRibbon', 820, 168, (c, w, h) => ribbon(c, w, h, 46))).setDepth(2));
    txt(scene, ctx, CX, 52, 'U P P E R', { fontFamily: 'Cormorant Garamond', fontStyle: 'bold', fontSize: '22px', color: GOLD });
    txt(scene, ctx, CX, 104, 'MORKEZELA', { fontFamily: 'Abril Fatface', fontSize: '74px', color: IVORY, shadow: { offsetX: 0, offsetY: 4, color: '#2a0309', blur: 0, fill: true } });
    // the subtitle on a little tab hanging from the ribbon
    ctx.add(scene.add.image(CX, 196, canvasTex(scene, 'mdTab', 230, 40, (c, w, h) => {
        c.fillStyle = CRIMSON_D; c.beginPath(); c.moveTo(0, 0); c.lineTo(w, 0); c.lineTo(w - 14, h); c.lineTo(14, h); c.closePath(); c.fill();
        c.strokeStyle = GOLD; c.lineWidth = 1.5; c.beginPath(); c.moveTo(20, h - 6); c.lineTo(w - 20, h - 6); c.stroke();
    })).setDepth(2));
    txt(scene, ctx, CX, 194, `~ ${ctx.subtitle} ~`, { fontFamily: 'Cormorant Garamond Italic', fontStyle: 'italic bold', fontSize: '21px', color: IVORY });

    // the footlight bar along the bottom, between Edgar and Ortolan
    const n = ctx.items.length, BW = 580, BY = 552;
    ctx.add(scene.add.image(CX, BY, canvasTex(scene, 'mdBar', BW + 40, 74, (c, w, h) => ribbon(c, w, h, 18))).setDepth(2));
    const cell = BW / n;
    for (let k = 1; k < n; k++) {
        ctx.add(scene.add.text(CX - BW / 2 + k * cell, BY - 3, '◆', { fontFamily: 'Cormorant Garamond', fontSize: '12px', color: GOLD }).setOrigin(0.5).setDepth(2));
    }
    ctx.items.forEach((item, i) => {
        let pill, label;
        entry(scene, ctx, i, CX - BW / 2 + (i + 0.5) * cell, BY - 3, cell - 14, 40, {
            build: (c) => {
                pill = scene.add.image(0, 0, canvasTex(scene, 'mdPill', 132, 34, (cx, w, h) => {
                    cx.fillStyle = IVORY; cx.beginPath(); cx.roundRect(1, 1, w - 2, h - 2, h / 2); cx.fill();
                    cx.strokeStyle = GOLD; cx.lineWidth = 2; cx.stroke();
                })).setAlpha(0).setDisplaySize(cell - 18, 34);
                label = scene.add.text(0, 0, item.label.toUpperCase(), { fontFamily: 'Cormorant Garamond', fontStyle: 'bold', fontSize: '16px', color: IVORY, letterSpacing: 1, padding: { x: 4, y: 3 } }).setOrigin(0.5);
                c.add([pill, label]);
            },
            focus: (on) => { tween(scene, pill, { alpha: on ? 1 : 0 }); label.setColor(on ? CRIMSON : IVORY); },
            press: () => tween(scene, label, { y: 2, yoyo: true, duration: 70 }),
            enable: (on) => label.setColor(on ? IVORY : '#a46a72')
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------
// 3. Bioluminiscence: neon on indigo

const CYAN = 0x5ef2ff, MAGENTA = 0xff4fd8;

function buildGlow(scene, ctx) {
    const { CX } = ctx;
    ctx.add(scene.add.image(CX, 250, canvasTex(scene, 'mdIndigo', 256, 256, (c, w, h) => {
        const g = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
        g.addColorStop(0, 'rgba(10,6,32,0.88)'); g.addColorStop(0.55, 'rgba(10,6,32,0.7)'); g.addColorStop(1, 'rgba(10,6,32,0)');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    })).setDisplaySize(880, 680).setDepth(1.9));
    txt(scene, ctx, CX, 58, 'U P P E R', { fontFamily: 'Comfortaa', fontStyle: 'bold', fontSize: '18px', color: '#ff7fe3' })
        .preFX.addGlow(MAGENTA, 3, 0, false, 0.1, 12);
    const title = txt(scene, ctx, CX, 112, 'MORKEZELA', { fontFamily: 'Monoton', fontSize: '66px', color: '#8ff7ff' });
    const fx = title.preFX.addGlow(CYAN, 4, 0, false, 0.1, 16);
    ctx.loop({ targets: fx, outerStrength: 7, duration: 2200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    txt(scene, ctx, CX, 178, ctx.subtitle.toLowerCase(), { fontFamily: 'Comfortaa', fontSize: '17px', color: '#cfc2ff', letterSpacing: 4 });

    const dot = canvasTex(scene, 'mdSporeDot', 24, 24, (c, w, h) => {
        const g = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
        g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.3, 'rgba(255,255,255,0.8)'); g.addColorStop(1, 'rgba(255,255,255,0)');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    });
    ctx.items.forEach((item, i) => {
        let label, glow, dots;
        entry(scene, ctx, i, CX, 276 + i * 58, 320, 46, {
            build: (c) => {
                label = scene.add.text(0, 0, item.label, { fontFamily: 'Comfortaa', fontStyle: 'bold', fontSize: '26px', color: '#ddd2ff', padding: { x: 8, y: 6 } }).setOrigin(0.5);
                glow = label.preFX.addGlow(0x9d7bff, 1.5, 0, false, 0.1, 10);
                const half = label.width / 2 + 22;
                dots = [-half, half].map(x => scene.add.image(x, 0, dot).setTint(CYAN).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0).setScale(0.8));
                c.add([label, ...dots]);
            },
            focus: (on) => {
                label.setColor(on ? '#9ffaff' : '#ddd2ff');
                glow.color = on ? CYAN : 0x9d7bff;
                tween(scene, glow, { outerStrength: on ? 4 : 1.5 });
                tween(scene, label.parentContainer, { scale: on ? 1.06 : 1 });
                dots.forEach(d => { scene.tweens.killTweensOf(d); d.setAlpha(on ? 1 : 0); if (on) ctx.loop({ targets: d, scale: 1.2, alpha: 0.5, duration: 600, yoyo: true, repeat: -1 }); });
            },
            press: () => tween(scene, label, { scale: 0.94, yoyo: true, duration: 70 }),
            enable: (on) => { label.setColor(on ? '#ddd2ff' : '#6b6294'); glow.outerStrength = on ? 1.5 : 0; }
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------
// 4. Brutal: a black slab, white condensed type, acid yellow

const ACID = '#e6ff2e';

function buildSlab(scene, ctx) {
    const X0 = 300, X1 = 772;
    ctx.add(scene.add.rectangle(X0, 0, X1 - X0, 240, 0x000000).setOrigin(0).setDepth(2));
    ctx.add(scene.add.rectangle(X0, 240, 6, 290, 0xe6ff2e).setOrigin(0).setDepth(2));          // the grid line down
    ctx.add(scene.add.text(X0 + 28, 26, 'UPPER', { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '20px', color: ACID, letterSpacing: 10 }).setDepth(2));
    ctx.add(scene.add.text(X0 + 22, 50, 'MORKEZELA', { fontFamily: 'Bebas Neue', fontSize: '122px', color: '#ffffff' }).setDepth(2));
    ctx.add(scene.add.rectangle(X0 + 30, 206, 10, 10, 0xe6ff2e).setOrigin(0, 0.5).setDepth(2));
    ctx.add(scene.add.text(X0 + 50, 206, ctx.subtitle.toUpperCase(), { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '15px', color: '#ffffff', letterSpacing: 6 }).setOrigin(0, 0.5).setDepth(2));

    const LABEL = { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '24px', color: '#ffffff', letterSpacing: 1 };
    ctx.items.forEach((item, i) => {
        let box, num, label;
        const y = 290 + i * 56;
        const probe = scene.make.text({ text: item.label.toUpperCase(), style: LABEL }, false);
        const bw = probe.width + 84, x = X0 + 6 + bw / 2;
        probe.destroy();
        entry(scene, ctx, i, x, y, bw, 44, {
            build: (c) => {
                box = scene.add.rectangle(-bw / 2, 0, bw, 44, 0x000000).setOrigin(0, 0.5);
                num = scene.add.text(-bw / 2 + 18, 0, `0${i + 1}`, { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '16px', color: ACID }).setOrigin(0, 0.5);
                label = scene.add.text(-bw / 2 + 58, 0, item.label.toUpperCase(), LABEL).setOrigin(0, 0.5);
                c.add([box, num, label]);
            },
            focus: (on) => {
                box.fillColor = on ? 0xe6ff2e : 0x000000;
                num.setColor(on ? '#000000' : ACID); label.setColor(on ? '#000000' : '#ffffff');
                tween(scene, label.parentContainer, { x: x + (on ? 14 : 0), duration: 120 });
            },
            press: () => tween(scene, label.parentContainer, { x: x + 26, yoyo: true, duration: 60 }),
            enable: (on) => { label.setColor(on ? '#ffffff' : '#5c5c5c'); num.setColor(on ? ACID : '#5c5c5c'); box.fillColor = on ? 0x000000 : 0x161616; }
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------
// 5. Úřad: a form card and a rubber stamp

const FORM = '#e5e9d4', TYPE = '#262626', STAMP = '#c4302b', BIRO = '#2448a8';

function buildOffice(scene, ctx) {
    const { CX } = ctx;
    const CW = 420, CH = 460;
    const ROWS = ctx.items.map((it, i) => -10 + i * 56);          // the rows' centres on the card
    const card = ctx.add(scene.add.container(CX + 6, 292).setDepth(2).setRotation(0.018));
    card.add(scene.add.image(0, 0, canvasTex(scene, 'mdForm', CW + 40, CH + 40, (c, w, h) => {
        const r = rng(52);
        c.save(); c.filter = 'blur(7px)'; c.fillStyle = 'rgba(0,0,0,0.5)'; c.fillRect(26, 30, CW, CH); c.restore();
        c.fillStyle = FORM; c.fillRect(20, 20, CW, CH);
        for (let k = 0; k < CW * CH / 30; k++) { c.fillStyle = `rgba(60,70,40,${0.02 + r() * 0.04})`; c.fillRect(20 + r() * CW, 20 + r() * CH, 1 + r() * 2, 1); }
        c.strokeStyle = 'rgba(40,60,70,0.55)'; c.lineWidth = 1.5; c.strokeRect(34, 34, CW - 28, CH - 28);
        c.strokeStyle = 'rgba(40,60,70,0.3)'; c.lineWidth = 1; c.strokeRect(38, 38, CW - 36, CH - 36);
        c.strokeStyle = 'rgba(70,90,110,0.25)';
        ROWS.forEach(ly => { const y = h / 2 + ly + 19; c.beginPath(); c.moveTo(50, y); c.lineTo(CW - 10, y); c.stroke(); });
        // a paper clip
        c.strokeStyle = '#8d949a'; c.lineWidth = 3; c.beginPath(); c.roundRect(58, 6, 22, 64, 11); c.stroke();
        c.beginPath(); c.roundRect(63, 14, 12, 44, 6); c.stroke();
    })));
    const L = -CW / 2 + 40;
    card.add(scene.add.text(L, -112, 'FORM 521-B', { fontFamily: 'Courier Prime Bold', fontSize: '20px', color: TYPE }).setOrigin(0, 0.5));
    card.add(scene.add.text(CW / 2 - 40, -112, 'No. 0177', { fontFamily: 'Courier Prime', fontSize: '18px', color: TYPE }).setOrigin(1, 0.5));
    card.add(scene.add.text(L, -84, `· ${ctx.subtitle} ·`, { fontFamily: 'Courier Prime', fontSize: '16px', color: '#4b4b4b' }).setOrigin(0, 0.5));
    // a scribbled signature at the bottom
    card.add(scene.add.image(CW / 2 - 110, CH / 2 - 26, canvasTex(scene, 'mdSignature', 150, 40, (c, w, h) => {
        c.strokeStyle = BIRO; c.lineWidth = 2; c.beginPath(); c.moveTo(4, 26);
        c.bezierCurveTo(20, 2, 30, 38, 46, 14); c.bezierCurveTo(56, 2, 60, 34, 78, 18); c.bezierCurveTo(92, 6, 104, 30, 146, 20); c.stroke();
    })));

    // the stamp, crooked, over the top of the card
    const stamp = canvasTex(scene, 'mdStamp', 470, 150, (c, w, h) => {
        const r = rng(77);
        c.strokeStyle = STAMP; c.fillStyle = STAMP;
        c.lineWidth = 6; c.beginPath(); c.roundRect(8, 8, w - 16, h - 16, 16); c.stroke();
        c.lineWidth = 2; c.beginPath(); c.roundRect(20, 20, w - 40, h - 40, 10); c.stroke();
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.font = '62px "Black Ops One"'; c.fillText('MORKEZELA', w / 2, 96);
        c.font = '20px "Black Ops One"'; c.fillText('★  UPPER  ★', w / 2, 46);
        c.globalCompositeOperation = 'destination-out';           // the worn rubber
        for (let k = 0; k < 900; k++) { c.fillStyle = `rgba(0,0,0,${0.4 + r() * 0.6})`; c.beginPath(); c.arc(r() * w, r() * h, r() * 1.8, 0, 7); c.fill(); }
        for (let k = 0; k < 12; k++) { c.fillStyle = 'rgba(0,0,0,0.5)'; c.fillRect(r() * w, r() * h, 20 + r() * 60, 1 + r() * 2); }
    });
    ctx.add(scene.add.image(CX - 4, 84, stamp).setRotation(-0.07).setAlpha(0.92).setDepth(2.1));

    const ROT = 0.018;
    ctx.items.forEach((item, i) => {
        let tick, label, strike;
        const lx = L + 150, ly = ROWS[i];
        entry(scene, ctx, i, card.x + lx * Math.cos(ROT) - ly * Math.sin(ROT), card.y + lx * Math.sin(ROT) + ly * Math.cos(ROT), 330, 44, {
            build: (c) => {
                c.setRotation(ROT);
                const box = scene.add.rectangle(-150, 0, 24, 24).setStrokeStyle(2, 0x262626);
                tick = scene.add.image(-150, -2, canvasTex(scene, 'mdTick', 34, 34, (cx, w, h) => {
                    cx.strokeStyle = BIRO; cx.lineWidth = 3.5; cx.lineCap = 'round';
                    cx.beginPath(); cx.moveTo(6, 7); cx.lineTo(28, 29); cx.moveTo(28, 6); cx.lineTo(7, 28); cx.stroke();
                })).setAlpha(0);
                label = scene.add.text(-118, 0, item.label, { fontFamily: 'Courier Prime Bold', fontSize: '24px', color: TYPE }).setOrigin(0, 0.5);
                strike = scene.add.rectangle(-118, 1, label.width, 2, 0x262626).setOrigin(0, 0.5).setVisible(false);
                c.add([box, tick, label, strike]);
            },
            focus: (on) => { tick.setAlpha(on ? 1 : 0); label.setColor(on ? BIRO : TYPE); },
            press: () => tween(scene, tick, { scale: 1.3, yoyo: true, duration: 70 }),
            enable: (on) => { label.setColor(on ? TYPE : '#8a8a80'); strike.setVisible(!on); }
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------
// 6. Vitráž: stained glass

const LEAD = '#17121f';
const GLASS = {
    violet: [[107, 58, 160], [83, 44, 140], [128, 76, 178], [70, 40, 120]],
    amber: [[240, 178, 60], [222, 150, 40], [250, 200, 90], [210, 130, 30]],
    teal: [[42, 140, 140], [30, 118, 128], [60, 160, 150], [24, 100, 112]],
    rose: [[201, 79, 124], [180, 60, 104], [220, 100, 140], [160, 50, 90]],
    grey: [[110, 106, 116], [96, 92, 102], [124, 120, 130], [86, 82, 92]]
};

/** a pane: the polygon shape filled with glass cells (nearest of n seeds), lead between them and round the edge */
function glassPane(ctx, w, h, shape, palette, seed, cells) {
    const r = rng(seed);
    const seeds = Array.from({ length: cells }, () => [r() * w, r() * h, palette[Math.floor(r() * palette.length)], 0.85 + r() * 0.3]);
    const img = ctx.createImageData(w, h);
    const owner = new Int16Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        let best = 0, bd = 1e9;
        for (let k = 0; k < seeds.length; k++) { const dx = seeds[k][0] - x, dy = (seeds[k][1] - y) * 1.4, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = k; } }
        owner[y * w + x] = best;
    }
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const k = owner[y * w + x], i = (y * w + x) * 4;
        const lead = (x > 0 && owner[y * w + x - 1] !== k) || (y > 0 && owner[(y - 1) * w + x] !== k)
            || (x > 1 && owner[y * w + x - 2] !== k) || (y > 1 && owner[(y - 2) * w + x] !== k);
        const [cr, cg, cb] = seeds[k][2], b = seeds[k][3] * (0.92 + 0.16 * Math.sin(x * 0.07 + y * 0.11 + k));
        img.data[i] = lead ? 23 : Math.min(255, cr * b); img.data[i + 1] = lead ? 18 : Math.min(255, cg * b);
        img.data[i + 2] = lead ? 31 : Math.min(255, cb * b); img.data[i + 3] = 255;
    }
    const tmp = document.createElement('canvas'); tmp.width = w; tmp.height = h;
    tmp.getContext('2d').putImageData(img, 0, 0);
    ctx.save(); shape(); ctx.clip(); ctx.drawImage(tmp, 0, 0);
    const g = ctx.createRadialGradient(w / 2, h * 0.35, 0, w / 2, h * 0.35, w * 0.6);       // light through the middle
    g.addColorStop(0, 'rgba(255,255,230,0.28)'); g.addColorStop(1, 'rgba(255,255,230,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
    ctx.restore();
    shape(); ctx.strokeStyle = LEAD; ctx.lineWidth = 7; ctx.stroke();
}

function buildGlass(scene, ctx) {
    const { CX } = ctx;
    const pointed = (c, w, h, tip) => () => {
        c.beginPath(); c.moveTo(4, h / 2); c.lineTo(tip, 4); c.lineTo(w - tip, 4); c.lineTo(w - 4, h / 2); c.lineTo(w - tip, h - 4); c.lineTo(tip, h - 4); c.closePath();
    };
    ctx.add(scene.add.image(CX, 104, canvasTex(scene, 'mdGlassTitle', 760, 170, (c, w, h) => {
        c.save(); c.filter = 'blur(8px)'; c.fillStyle = 'rgba(0,0,0,0.6)'; pointed(c, w, h, 52)(); c.fill(); c.restore();
        glassPane(c, w, h, pointed(c, w, h, 52), GLASS.violet, 11, 46);
    })).setDepth(2));
    txt(scene, ctx, CX, 50, 'U P P E R', { fontFamily: 'Cinzel', fontStyle: 'bold', fontSize: '20px', color: '#fbeec8', stroke: LEAD, strokeThickness: 5 });
    txt(scene, ctx, CX, 110, 'Morkezela', { fontFamily: 'UnifrakturMaguntia', fontSize: '84px', color: '#ffcf5a', stroke: LEAD, strokeThickness: 9 });
    ctx.add(scene.add.rectangle(CX, 202, 250, 30, 0x17121f).setDepth(2));
    txt(scene, ctx, CX, 202, ctx.subtitle.toUpperCase(), { fontFamily: 'Cinzel', fontStyle: 'bold', fontSize: '15px', color: '#e8d9ff', letterSpacing: 3 });

    const hues = ['amber', 'teal', 'rose', 'violet'];
    ctx.items.forEach((item, i) => {
        let pane, grey, light, label;
        entry(scene, ctx, i, CX, 274 + i * 62, 330, 52, {
            build: (c) => {
                const key = 'mdGlassPane' + i;
                pane = scene.add.image(0, 0, canvasTex(scene, key, 340, 58, (cx, w, h) => glassPane(cx, w, h, pointed(cx, w, h, 24), GLASS[hues[i % 4]], 30 + i, 16)));
                grey = scene.add.image(0, 0, canvasTex(scene, key + 'Grey', 340, 58, (cx, w, h) => glassPane(cx, w, h, pointed(cx, w, h, 24), GLASS.grey, 30 + i, 16))).setVisible(false);
                light = scene.add.image(0, 0, key).setTintFill(0xffffff).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0);
                label = scene.add.text(0, 0, item.label, { fontFamily: 'Cinzel', fontStyle: 'bold', fontSize: '22px', color: '#fff6dc', stroke: LEAD, strokeThickness: 5 }).setOrigin(0.5);
                c.add([pane, grey, light, label]);
            },
            focus: (on) => { tween(scene, light, { alpha: on ? 0.22 : 0 }); label.setColor(on ? '#ffd86b' : '#fff6dc'); tween(scene, label.parentContainer, { scale: on ? 1.04 : 1 }); },
            press: () => tween(scene, light, { alpha: 0.5, yoyo: true, duration: 70 }),
            enable: (on) => { pane.setVisible(on); grey.setVisible(!on); label.setColor(on ? '#fff6dc' : '#a9a3b0'); }
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------
// 7. Brutal in a band (after Armello's side menu and Dread Nautical's bottom bar): the painting whole, the menu in black

export const BOTTOM_BAND = 80;          // the bottom layout's band height (screen px)

/** where the painting goes (top-left, scale) for a layout; band = layers.json's band { w, h, spireTop } */
export function paintingLayout(kind, W, H, band) {
    if (kind === 'right') return { x: 0, y: 0, scale: H / band.h };
    if (kind === 'left') return { x: W - band.w * H / band.h, y: 0, scale: H / band.h };
    if (kind === 'bottom') return { x: 0, y: 0, scale: (H - BOTTOM_BAND) / band.h };
    return { x: Math.floor((W - band.w) / 2), y: -band.spireTop, scale: 1 };       // 'full'
}

const RULE = 4;
const LABEL_STYLE = { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '19px', color: '#ffffff', letterSpacing: 1 };

/** a text shrunk (or grown) to exactly maxW wide */
function fitWidth(t, maxW) {
    t.setFontSize(Math.floor(parseFloat(t.style.fontSize) * maxW / t.width));
    return t;
}

/** the title lockup (UPPER, MORKEZELA fitted to w, an acid bar) at x, y; returns its bottom */
function brutalTitle(scene, ctx, x, y, w) {
    ctx.add(scene.add.text(x, y, 'UPPER', { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '14px', color: ACID, letterSpacing: 9 }).setDepth(2));
    const t = ctx.add(fitWidth(scene.add.text(x, y + 14, 'MORKEZELA', { fontFamily: 'Bebas Neue', fontSize: '100px', color: '#ffffff', padding: { y: 4 } }), w).setDepth(2));
    const bottom = t.y + t.height - 2;
    ctx.add(scene.add.rectangle(x, bottom + 4, 30, 4, 0xe6ff2e).setOrigin(0).setDepth(2));
    return bottom + 8;
}

function buildBandSide(scene, ctx, side) {
    const { W, H, painting: P } = ctx;
    const X0 = side === 'right' ? Math.floor(P.x + P.w) : 0;
    const BW = side === 'right' ? W - X0 : Math.ceil(P.x);
    ctx.add(scene.add.rectangle(X0, 0, BW, H, 0x000000).setOrigin(0).setDepth(1.8));
    ctx.add(scene.add.rectangle(side === 'right' ? X0 : X0 + BW - RULE, 0, RULE, H, 0xe6ff2e).setOrigin(0).setDepth(1.85));
    const RX = side === 'right' ? X0 + RULE : X0;             // the rows' left edge (from the rule) and width
    const RW = BW - RULE;
    const IX = RX + 20, IW = RW - 40;
    brutalTitle(scene, ctx, IX, 30, IW);

    // the footer: the subtitle
    ctx.add(scene.add.rectangle(IX, H - 32, 8, 8, 0xe6ff2e).setOrigin(0, 0.5).setDepth(2));
    ctx.add(scene.add.text(IX + 16, H - 32, ctx.subtitle.toUpperCase(), { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '11px', color: '#9a9a9a', letterSpacing: 4 }).setOrigin(0, 0.5).setDepth(2));

    // the menu: full-width rows in the middle; the focused one turns acid and joins the rule
    const ROW = 46, GAP = 8, n = ctx.items.length;
    const top = Math.round((H - (n * ROW + (n - 1) * GAP)) / 2) + 30;
    ctx.items.forEach((item, i) => {
        let fill, num, label, arrow;
        const y = top + i * (ROW + GAP) + ROW / 2;
        entry(scene, ctx, i, RX + RW / 2, y, RW, ROW, {
            build: (c) => {
                fill = scene.add.rectangle(-RW / 2, 0, RW, ROW, 0x000000).setOrigin(0, 0.5);
                num = scene.add.text(-RW / 2 + 20, 0, `0${i + 1}`, { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '13px', color: ACID }).setOrigin(0, 0.5);
                label = scene.add.text(-RW / 2 + 50, 0, item.label.toUpperCase(), LABEL_STYLE).setOrigin(0, 0.5);
                arrow = scene.add.triangle(RW / 2 - 18, 0, 0, -6, 0, 6, 9, 0, 0x000000).setVisible(false);
                c.add([fill, num, label, arrow]);
            },
            focus: (on) => {
                fill.fillColor = on ? 0xe6ff2e : 0x000000;
                num.setColor(on ? '#000000' : ACID);
                label.setColor(on ? '#000000' : '#ffffff');
                arrow.setVisible(on);
                tween(scene, label, { x: -RW / 2 + 50 + (on ? 6 : 0), duration: 110 });
            },
            press: () => tween(scene, arrow, { x: RW / 2 - 12, yoyo: true, duration: 70 }),
            enable: (on) => { label.setColor(on ? '#ffffff' : '#555555'); num.setColor(on ? ACID : '#555555'); }
        });
    });
}

function buildBandBottom(scene, ctx) {
    const { W, H, painting: P } = ctx;
    const PW = Math.floor(P.w), PH = Math.floor(P.h);
    // the black: a title column right of the painting and the band under it, an acid L between
    ctx.add(scene.add.rectangle(PW, 0, W - PW, PH, 0x000000).setOrigin(0).setDepth(1.8));
    ctx.add(scene.add.rectangle(0, PH, W, H - PH, 0x000000).setOrigin(0).setDepth(1.8));
    ctx.add(scene.add.rectangle(PW, 0, RULE, PH, 0xe6ff2e).setOrigin(0).setDepth(1.85));
    ctx.add(scene.add.rectangle(0, PH, W, RULE, 0xe6ff2e).setOrigin(0).setDepth(1.85));
    const IX = PW + RULE + 28, IW = W - IX - 28;
    const tb = brutalTitle(scene, ctx, IX, 34, IW);
    ctx.add(scene.add.text(IX + 42, tb - 2, ctx.subtitle.toUpperCase(), { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '12px', color: '#ffffff', letterSpacing: 5 }).setOrigin(0, 0.5).setDepth(2));
    // the focused entry's number, huge, at the foot of the column
    const big = ctx.add(scene.add.text(W - 24, PH + 14, '', { fontFamily: 'Bebas Neue', fontSize: '210px', color: ACID, padding: { y: 6 } }).setOrigin(1, 1).setDepth(2));
    const of = ctx.add(scene.add.text(IX, PH - 22, `/ 0${ctx.items.length}`, { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '14px', color: '#5a5a5a', letterSpacing: 3 }).setOrigin(0, 0.5).setDepth(2));
    of.setVisible(false);

    // the menu along the band: cells; the focused one is an acid parallelogram
    const n = ctx.items.length, M = 20, CW = (W - 2 * M) / n, BY = PH + RULE + (H - PH - RULE) / 2, BH = H - PH - RULE - 18;
    ctx.items.forEach((item, i) => {
        let slant, num, label;
        entry(scene, ctx, i, M + (i + 0.5) * CW, BY, CW - 8, BH, {
            build: (c) => {
                const w = CW - 16, k = 14;
                slant = scene.add.graphics().fillStyle(0xe6ff2e, 1)
                    .fillPoints([{ x: -w / 2 + k, y: -BH / 2 }, { x: w / 2, y: -BH / 2 }, { x: w / 2 - k, y: BH / 2 }, { x: -w / 2, y: BH / 2 }], true)
                    .setVisible(false);
                label = scene.add.text(10, 0, item.label.toUpperCase(), { ...LABEL_STYLE, fontSize: '20px' }).setOrigin(0.5);
                num = scene.add.text(label.x - label.width / 2 - 8, 1, `0${i + 1}`, { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '12px', color: ACID }).setOrigin(1, 0.5);
                c.add([slant, num, label]);
            },
            focus: (on) => {
                slant.setVisible(on);
                num.setColor(on ? '#000000' : ACID);
                label.setColor(on ? '#000000' : '#ffffff');
                if (on) { big.setText(`0${i + 1}`); of.setVisible(true); }
            },
            press: () => tween(scene, label, { y: 2, yoyo: true, duration: 60 }),
            enable: (on) => { label.setColor(on ? '#ffffff' : '#555555'); num.setColor(on ? ACID : '#555555'); }
        });
    });
}

export const MENU_DESIGNS = {
    bandRight: { name: 'Brutal · pás vpravo', layout: 'right', build: (scene, ctx) => buildBandSide(scene, ctx, 'right') },
    bandLeft: { name: 'Brutal · pás vlevo', layout: 'left', build: (scene, ctx) => buildBandSide(scene, ctx, 'left') },
    bandBottom: { name: 'Brutal · pás dole', layout: 'bottom', build: buildBandBottom },
    paper: { name: 'Ateliér (papír a páska)', build: buildPaper },
    cabaret: { name: 'Kabaret', build: buildCabaret },
    glow: { name: 'Bioluminiscence', build: buildGlow },
    slab: { name: 'Brutal', build: buildSlab },
    office: { name: 'Úřad', build: buildOffice },
    glass: { name: 'Vitráž', build: buildGlass }
};
