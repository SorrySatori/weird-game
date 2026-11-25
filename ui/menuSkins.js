/**
 * menuSkins.js — the main menu's looks drawn as art (ui/mainMenuBand.js), "industrial crossed with biomechanics and
 * fungi", tried 2026-11-24. 'jungle' is THE menu (picked 2026-11-24); the others stay as trials (ui/mainMenuBand.js
 * menuTrials(), tools/menu_trials/README.md). The art is drawn by tools/artgen/menu_skins.py into
 * assets/images/ui/menu/skins/<skin>/ (bands, panels, rules, nine-slice plates, titles); the life is added here:
 *
 *   rust     corrugated rusty sheet, wires, weeds; the entries scrap plates with caged lamps that flicker on, a click
 *            showers welding sparks; the title stencilled on a rusty sign (Saira Stencil One + Saira Condensed)
 *   biomech  bone and blackened metal, a spine for the rule; the entries ribbed pods whose slit glows red with a
 *            heartbeat, a click spatters lymph; the title cast in Grenze Gotisch, its glow beating (+ Grenze)
 *   jungle   crumbling concrete, ivy, a verdigris drainpipe, mycelium glowing in the cracks and breathing; the
 *            entries cracked slabs the mycelium lights up, glowing mushrooms sprout (Bungee + Rubik)
 *   crazy    a living machine: veined flesh stitched with wire, eyes that follow the pointer and blink, teeth along
 *            the rule; the entries tags hanging on strings, swinging, their letters dancing, an eye popping out; the
 *            title a ransom note of nine fonts that wobble, its O an eye (Rubik Beastly + Rubik)
 *   tripe    the tripe fungus (Auricularia mesenterica): wrinkled wet lobes, pale hairy margins; the entries jiggle
 *            like jelly and glisten; the title grows out of the fungus, breathes and drips (Fraunces)
 *   panelak  a grimy post-Soviet prefab tower at dusk: windows lit one by one, a TV flickering, an aviation light; a
 *            lattice girder for the rule; the entries glass blocks (luxfery) in steel frames, their labels neon tubes:
 *            focus = the stairwell switch, the tube behind the glass strikes, the neon lights; the name in rooftop
 *            letters with red neon (one broken), UPPER in cold white neon, the subtitle on a backlit shop sign
 *            (Russo One + Jost)
 *
 * mainMenuBand.js calls a skin's hooks with its kit K (navEntry, tex, glowTex, shroom, tween, pulseDown, DEPTH,
 * RULE, TH, ...), so this file does not import it back. A skin: { data (the theme's colours and faces), preload,
 * band, rule, panelBg, entry, title, myc (the band's mycelium threads: false = hidden, or their alpha range) }.
 */

const DIR = 'assets/images/ui/menu/skins/';
const key = (skin, name) => `sk_${skin}_${name}`;

function loadImages(scene, skin, names) {
    names.forEach((n) => {
        const k = key(skin, n);
        if (scene.textures.exists(k)) return;
        scene.load.image(k, `${DIR}${skin}/${n}.png`);
        // not pixel art: smooth when it jiggles, swings, breathes (the game's pixelArt makes textures NEAREST)
        scene.load.once(`filecomplete-image-${k}`, () => scene.textures.get(k).setFilter(Phaser.Textures.FilterMode.LINEAR));
    });
}

function loadFonts(scene, fonts) {
    fonts.forEach(([family, file, desc]) => {
        if ([...document.fonts].some(f => f.family.replace(/"/g, '') === family && f.status === 'loaded')) return;
        scene.load.font(family, 'assets/fonts/' + file, 'truetype', desc);
    });
}

/** run fn(t in s) every frame until the scene shuts down */
function onUpdate(scene, fn) {
    const t0 = scene.time.now;
    let last = t0;
    const tick = () => { const now = scene.time.now; fn((now - t0) / 1000, (now - last) / 1000); last = now; };
    scene.events.on('update', tick);
    scene.events.once('shutdown', () => scene.events.off('update', tick));
}

/** the band's texture (the main menu's narrow one or the pause menu's wide one), cut at the rule */
function bandImage(scene, skin, RX, H, depth) {
    const name = RX + 4 <= 224 ? 'band' : 'band_wide';
    return { img: scene.add.image(0, 0, key(skin, name)).setOrigin(0).setDepth(depth).setCrop(0, 0, RX, H), name };
}

/** a panel's texture inside its body container (under the rows) */
function panelImage(scene, skin, w, H) {
    return scene.add.image(0, 0, key(skin, 'panel')).setOrigin(0).setCrop(0, 0, w, H);
}

/** a rule image cut to h (a centred card's edges are shorter than the screen) */
const cut = (img, h) => img.setCrop(0, 0, img.width, Math.min(h, img.height));

const plate = (scene, skin, name, w, h, side, tb) => scene.add.nineslice(0, 0, key(skin, name), null, w, h, side, side, tb, tb);

/** sparks / droplets / confetti flung from a point (one emitter per scene and look) */
function burst(scene, K, id, cfg) {
    const k = '_skinBurst_' + id;
    if (!scene[k] || !scene[k].active) {
        K.sporeTex(scene);
        scene[k] = scene.add.particles(0, 0, 'mmSpore', { emitting: false, ...cfg }).setDepth(K.DEPTH.ui + 0.2);
        scene.events.once('shutdown', () => { scene[k] = null; });
    }
    return scene[k];
}

/**
 * The common entry: a nine-slice plate the width of the band, a label on it, optionally a glow layer (the plate's
 * glow mask, tinted, ADD) that o.glowPulse animates while focused; o.build / o.focus / o.press add the rest.
 */
function plateEntry(scene, K, nav, { item, i, RX, y, ROW, garden, at }, o) {
    const PW = RX - 22;
    const P = { PW, ROW, y, RX };
    const h = K.navEntry(scene, nav, RX / 2, y, RX, ROW, {
        build: (c) => {
            P.c = c;
            P.plate = plate(scene, o.skin, o.plate(i), PW, ROW, o.side, o.tb);
            P.glow = o.glow ? plate(scene, o.skin, o.glow(i), PW, ROW, o.side, o.tb).setTint(o.glowColour)
                .setBlendMode(Phaser.BlendModes.ADD).setAlpha(0) : null;
            P.label = scene.add.text(o.labelDx || 0, 0, o.upper ? item.label.toUpperCase() : item.label, { ...o.labelStyle, padding: { x: 4, y: 3 } })
                .setOrigin(0.5);
            const px = parseInt(o.labelStyle.fontSize, 10);
            for (let fs = px; P.label.width > PW - (o.labelRoom || 40) && fs > 11; fs--) P.label.setFontSize(fs - 1);
            const under = [], over = [];
            o.build?.(P, under, over);
            c.add([...under, P.plate, ...(P.glow ? [P.glow] : []), P.label, ...over]);
        },
        focus: (on) => {
            P.label.setColor(on ? o.labelOn : o.labelColour);
            if (P.glow) {
                scene.tweens.killTweensOf(P.glow);
                if (on) o.glowPulse(P.glow); else P.glow.setAlpha(0);
            }
            o.focus?.(P, on);
        },
        press: () => {
            o.press?.(P);
            K.pulseDown(scene, RX, y, garden, at);
        },
        enable: (on) => {
            P.plate.setTint(on ? 0xffffff : (o.offTint ?? 0x5a5a5a));
            P.label.setColor(on ? o.labelColour : o.labelDim);
            o.enable?.(P, on);
        },
        action: item.action
    });
    h.container.setDepth(K.DEPTH.ui);
    h.setEnabled(item.enabled !== false);
    return { handle: h };
}

/** little mushrooms that sprout on a focused entry's top edge (the Brutal band's, in the skin's colours) */
function sprouts(scene, K, P, colours, glowColour, over) {
    P.sglow = scene.add.image(P.PW / 2 - 34, -P.ROW / 2 - 4, K.glowTex(scene)).setTint(glowColour)
        .setBlendMode(Phaser.BlendModes.ADD).setDisplaySize(64, 30).setAlpha(0);
    P.shrooms = [[-48, 1, 0.7], [-37, 0, 0.85], [-26, 2, 0.65]].map(([dx, kind, s], j) =>
        scene.add.image(P.PW / 2 + dx, -P.ROW / 2 + 3, K.shroom(scene, kind)).setOrigin(0.5, 1)
            .setTint(colours[j % colours.length]).setScale(0).setData('s', s));
    over.unshift(P.sglow, ...P.shrooms);
}
function sproutsFocus(scene, P, on) {
    P.shrooms.forEach((s, j) => {
        scene.tweens.killTweensOf(s);
        scene.tweens.add(on
            ? { targets: s, scale: s.getData('s'), duration: 260, delay: j * 55, ease: 'Back.easeOut' }
            : { targets: s, scale: 0, duration: 120, ease: 'Sine.easeIn' });
    });
    scene.tweens.killTweensOf(P.sglow);
    if (on) scene.tweens.add({ targets: P.sglow, alpha: { from: 0.2, to: 0.6 }, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    else P.sglow.setAlpha(0);
}

/** a heartbeat (lub-dub, rest) on a target's property, forever */
function heartbeat(scene, target, prop, lo, hi) {
    return scene.tweens.chain({
        targets: target, loop: -1, tweens: [
            { [prop]: hi, duration: 90, ease: 'Sine.easeOut' },
            { [prop]: lo + (hi - lo) * 0.35, duration: 120, ease: 'Sine.easeIn' },
            { [prop]: hi * 0.95, duration: 90, ease: 'Sine.easeOut' },
            { [prop]: lo, duration: 600, ease: 'Sine.easeIn' }
        ]
    });
}

// =====================================================================================================================
// RUST

const SODIUM = 0xff9638;
const rust = {
    data: {
        accent: SODIUM, bg: 0x17110e, onFill: 0x4a2412, onText: '#ffb057', onIcon: 0xffb057,
        text: 0xe8dcc4, dim: 0x6a5e54, note: 0xa89580, rowBand: 0x2a1c14, track: 0x4a3a30, off: 0x5e5048,
        font: 'Saira Condensed', head: 'Saira Stencil One', headBold: false, headScale: 0.72, labelPx: 21, rowPx: 17, smallSpacing: 3,
        thread: SODIUM, garden: [0xc86a2c, 0xe0a040, 0x9a6a4a], glow: SODIUM, spore: 0xffc070, basket: 0xc84a2a, mycena: 0xffb050
    },
    myc: false,
    preload(scene) {
        loadFonts(scene, [['Saira Stencil One', 'SairaStencilOne.ttf'], ['Saira Condensed', 'SairaCondensed-Bold.ttf', { weight: '700' }]]);
        loadImages(scene, 'rust', ['band', 'band_wide', 'panel', 'rule', 'plate0', 'plate1', 'plate2', 'plate3', 'plate4', 'lamp_off', 'lamp_on', 'title']);
    },
    rule(scene, K, x, h) {
        return cut(scene.add.image(x + K.RULE / 2, 0, key('rust', 'rule')).setOrigin(0.5, 0), h);
    },
    band(scene, K, { RX, H, depth }) {
        bandImage(scene, 'rust', RX, H, depth);
        this.rule(scene, K, RX, H).setDepth(depth + 0.05);
    },
    panelBg(scene, K, w, H) { return [panelImage(scene, 'rust', w, H)]; },
    entry(scene, K, nav, ctx) {
        const sparks = burst(scene, K, 'rust', {
            speed: { min: 60, max: 200 }, angle: { min: 200, max: 340 }, lifespan: { min: 300, max: 750 }, gravityY: 520,
            scale: { start: 1, end: 0.2 }, alpha: { start: 1, end: 0.2 }, tint: [0xfff2c0, 0xffd27a, SODIUM]
        });
        return plateEntry(scene, K, nav, ctx, {
            skin: 'rust', plate: (i) => 'plate' + (i % 5), side: 14, tb: 12, upper: true, labelDx: -8, labelRoom: 56,
            labelStyle: { fontFamily: 'Saira Condensed', fontStyle: 'bold', fontSize: '21px', color: '#e8dcc4', stroke: '#0c0908', strokeThickness: 4, letterSpacing: 1 },
            labelColour: '#e8dcc4', labelOn: '#ffb057', labelDim: '#6a5e54',
            build(P, under, over) {
                const lx = P.PW / 2 - 18, ly = -P.ROW / 2 - 4;
                P.light = scene.add.image(lx - 30, -2, K.glowTex(scene)).setTint(SODIUM).setBlendMode(Phaser.BlendModes.ADD)
                    .setDisplaySize(190, 80).setAlpha(0);
                P.lampOff = scene.add.image(lx, ly, key('rust', 'lamp_off')).setOrigin(0.5, 0);
                P.lampOn = scene.add.image(lx, ly, key('rust', 'lamp_on')).setOrigin(0.5, 0).setAlpha(0);
                P.halo = scene.add.image(lx, ly + 14, K.glowTex(scene)).setTint(SODIUM).setBlendMode(Phaser.BlendModes.ADD)
                    .setDisplaySize(60, 60).setAlpha(0);
                over.push(P.light, P.lampOff, P.lampOn, P.halo);
            },
            focus(P, on) {
                scene.tweens.killTweensOf([P.lampOn, P.halo, P.light]);
                if (!on) { P.lampOn.setAlpha(0); P.halo.setAlpha(0); P.light.setAlpha(0); return; }
                // a sodium lamp striking: a flicker, then on, humming
                scene.tweens.chain({ targets: P.lampOn, tweens: [
                    { alpha: 1, duration: 40 }, { alpha: 0.15, duration: 60 }, { alpha: 1, duration: 40 },
                    { alpha: 0.4, duration: 80 }, { alpha: 1, duration: 60 }] });
                scene.tweens.add({ targets: P.halo, alpha: { from: 0.5, to: 0.8 }, duration: 700, yoyo: true, repeat: -1, delay: 280 });
                scene.tweens.add({ targets: P.light, alpha: { from: 0.18, to: 0.28 }, duration: 900, yoyo: true, repeat: -1, delay: 280 });
            },
            press(P) { sparks.explode(22, ctx.RX / 2 + P.PW / 2 - 18, P.y - P.ROW / 2 + 10); }
        });
    },
    title(scene, K, x) {
        const d = K.DEPTH.title;
        scene.add.image(x, 6, key('rust', 'title')).setOrigin(0.5, 0).setDepth(d);
        // a sodium glow over the sign's top, humming
        const g = scene.add.image(x, 40, K.glowTex(scene)).setTint(SODIUM).setBlendMode(Phaser.BlendModes.ADD)
            .setDisplaySize(260, 70).setAlpha(0.1).setDepth(d + 0.01);
        scene.tweens.add({ targets: g, alpha: 0.2, duration: 1700, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    }
};

// =====================================================================================================================
// BIOMECH

const LYMPH = 0xe8364f;
const biomech = {
    data: {
        accent: LYMPH, bg: 0x0d0c0c, onFill: 0x3e0b15, onText: '#ffd6dc', onIcon: 0xffb0bc,
        text: 0xddd3be, dim: 0x5e5850, note: 0xa39a88, rowBand: 0x221a1a, track: 0x3e3836, off: 0x5a5250,
        font: 'Grenze', head: 'Grenze Gotisch', headBold: true, headScale: 0.78, labelPx: 20, rowPx: 17, smallSpacing: 2,
        thread: LYMPH, garden: [0xd8cdb4, LYMPH, 0x9a8f7a], glow: LYMPH, spore: 0xffb0bc, basket: LYMPH, mycena: 0xd8cdb4
    },
    myc: false,
    preload(scene) {
        loadFonts(scene, [['Grenze Gotisch', 'GrenzeGotisch.ttf', { weight: '100 900' }], ['Grenze', 'Grenze.ttf', { weight: '100 900' }]]);
        loadImages(scene, 'biomech', ['band', 'band_wide', 'panel', 'rule', 'plate0', 'plate1', 'plate2', 'plate3', 'plate4', 'plate_glow', 'title']);
    },
    rule(scene, K, x, h) {
        return cut(scene.add.image(x + K.RULE / 2, 0, key('biomech', 'rule')).setOrigin(0.5, 0), h);
    },
    band(scene, K, { RX, H, depth }) {
        bandImage(scene, 'biomech', RX, H, depth);
        const r = this.rule(scene, K, RX, H).setDepth(depth + 0.05);
        // the lymph in the spine's vein beats
        const v = scene.add.rectangle(r.x - r.width / 2 + 2.5, 0, 3, H, LYMPH).setOrigin(0.5, 0).setBlendMode(Phaser.BlendModes.ADD)
            .setAlpha(0.15).setDepth(depth + 0.06);
        heartbeat(scene, v, 'alpha', 0.12, 0.55);
    },
    panelBg(scene, K, w, H) { return [panelImage(scene, 'biomech', w, H)]; },
    entry(scene, K, nav, ctx) {
        const drops = burst(scene, K, 'biomech', {
            speed: { min: 40, max: 150 }, angle: { min: 200, max: 340 }, lifespan: { min: 400, max: 900 }, gravityY: 380,
            scale: { start: 1.4, end: 0.6 }, alpha: { start: 1, end: 0.3 }, tint: [LYMPH, 0xa0102a, 0xff7a8c]
        });
        let beat = null;
        return plateEntry(scene, K, nav, ctx, {
            skin: 'biomech', plate: (i) => 'plate' + (i % 5), glow: () => 'plate_glow', glowColour: LYMPH, side: 30, tb: 10,
            labelStyle: { fontFamily: 'Grenze', fontStyle: 'bold', fontSize: '20px', color: '#ddd3be', stroke: '#0a0808', strokeThickness: 4 },
            labelColour: '#ddd3be', labelOn: '#ffe6ea', labelDim: '#5e5850', labelRoom: 64,
            glowPulse: (g) => heartbeat(scene, g, 'alpha', 0.35, 0.9),
            focus(P, on) {
                beat?.stop(); beat = null;
                P.c.setScale(1);
                if (on) beat = heartbeat(scene, P.c, 'scale', 1, 1.03);
            },
            press(P) { drops.explode(16, ctx.RX / 2, P.y); }
        });
    },
    title(scene, K, x) {
        const d = K.DEPTH.title;
        scene.add.image(x, 6, key('biomech', 'title')).setOrigin(0.5, 0).setDepth(d);
        const g = scene.add.image(x, 78, K.glowTex(scene)).setTint(LYMPH).setBlendMode(Phaser.BlendModes.ADD)
            .setDisplaySize(400, 80).setAlpha(0.1).setDepth(d + 0.01);
        heartbeat(scene, g, 'alpha', 0.08, 0.3);
    }
};

// =====================================================================================================================
// JUNGLE

const MINT = 0x96ffc4;
const jungle = {
    data: {
        accent: MINT, bg: 0x151816, onFill: 0x1d3a28, onText: '#b4ffd6', onIcon: MINT,
        text: 0xdfe2d2, dim: 0x5c625a, note: 0x9aa494, rowBand: 0x222a24, track: 0x3a443c, off: 0x56605a,
        font: 'Rubik', head: 'Bungee', headBold: false, headScale: 0.6, labelPx: 18, rowPx: 16, smallSpacing: 3,
        thread: MINT, garden: [MINT, 0x5fd6a0, 0xe8fff0], glow: MINT, spore: 0xc8ffe0, basket: 0xd2577f, mycena: MINT
    },
    myc: false,             // the band's own texture grows mould colonies; thin threads off the rule read as sparks
    preload(scene) {
        loadFonts(scene, [['Bungee', 'Bungee.ttf'], ['Rubik', 'Rubik.ttf', { weight: '300 900' }]]);
        loadImages(scene, 'jungle', ['band', 'band_wide', 'panel', 'band_myc', 'band_wide_myc', 'panel_myc', 'rule', 'title',
            'title_myc', 'ivy_l', 'ivy_r', ...[0, 1, 2, 3, 4].flatMap(i => ['plate' + i, `plate${i}_glow`])]);
    },
    rule(scene, K, x, h) {
        return cut(scene.add.image(x + K.RULE / 2, 0, key('jungle', 'rule')).setOrigin(0.5, 0), h);
    },
    /** the mycelium in the cracks, glowing and breathing */
    breathe(scene, img, from = 0.35, to = 0.85, ms = 2600) {
        img.setTint(MINT).setBlendMode(Phaser.BlendModes.ADD).setAlpha(from);
        scene.tweens.add({ targets: img, alpha: to, duration: ms, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        return img;
    },
    band(scene, K, { RX, H, depth }) {
        const { name } = bandImage(scene, 'jungle', RX, H, depth);
        this.breathe(scene, scene.add.image(0, 0, key('jungle', name + '_myc')).setOrigin(0).setCrop(0, 0, RX, H).setDepth(depth + 0.01));
        this.rule(scene, K, RX, H).setDepth(depth + 0.05);
    },
    panelBg(scene, K, w, H) {
        return [panelImage(scene, 'jungle', w, H), this.breathe(scene, scene.add.image(0, 0, key('jungle', 'panel_myc')).setOrigin(0).setCrop(0, 0, w, H))];
    },
    entry(scene, K, nav, ctx) {
        return plateEntry(scene, K, nav, ctx, {
            skin: 'jungle', plate: (i) => 'plate' + (i % 5), glow: (i) => `plate${i % 5}_glow`, glowColour: MINT, side: 12, tb: 10,
            labelStyle: { fontFamily: 'Rubik', fontStyle: 'bold', fontSize: '18px', color: '#dfe2d2', stroke: '#0e120f', strokeThickness: 4 },
            // a disabled entry: the slab a shade darker, its label muted but readable, ivy grown over its ends
            labelColour: '#dfe2d2', labelOn: '#b4ffd6', labelDim: '#8d9488', offTint: 0x6a6a6a,
            glowPulse: (g) => scene.tweens.add({ targets: g, alpha: { from: 0.45, to: 1 }, duration: 1300, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }),
            build(P, under, over) {
                sprouts(scene, K, P, [MINT, 0xe8fff0, 0x5fd6a0], MINT, over);
                P.ivy = [scene.add.image(-P.PW / 2 - 3, 0, key('jungle', 'ivy_l')).setOrigin(0, 0.5),
                    scene.add.image(P.PW / 2 + 3, 0, key('jungle', 'ivy_r')).setOrigin(1, 0.5)];
                over.push(...P.ivy);
            },
            enable(P, on) { P.ivy.forEach(v => v.setVisible(!on)); },
            focus(P, on) { sproutsFocus(scene, P, on); },
            press(P) { ctx.puff.explode(14, ctx.RX / 2 + P.PW / 2 - 36, P.y - P.ROW / 2 - 6); }
        });
    },
    title(scene, K, x) {
        const d = K.DEPTH.title;
        scene.add.image(x, 6, key('jungle', 'title')).setOrigin(0.5, 0).setDepth(d);
        // the mycelium tufts in the lintel's cracks, breathing slowly
        this.breathe(scene, scene.add.image(x, 6, key('jungle', 'title_myc')).setOrigin(0.5, 0).setDepth(d + 0.01), 0.25, 0.9, 3400);
        K.sporeTex(scene);
        scene.add.particles(0, 0, 'mmSpore', {
            x: { min: x - 220, max: x + 220 }, y: { min: 30, max: 110 }, speedY: { min: -14, max: -5 }, speedX: { min: -5, max: 5 },
            lifespan: { min: 2400, max: 4200 }, frequency: 260, scale: { start: 0.9, end: 0.3 }, alpha: { start: 0.8, end: 0 }, tint: 0xc8ffe0
        }).setDepth(d + 0.02);
    }
};

// =====================================================================================================================
// CRAZY

const PINK = 0xff3fa4, ACIDG = 0xc8ff00, CYANC = 0x50f0ff;
const INKS = ['#1c0a1c', '#8a0a44', '#0a3c5e', '#3a1a6e', '#1c4a0a'];

/**
 * An eye: its ball and iris (the big one in the title), the iris rolling toward the pointer, blinking now and
 * then. In a container (a panel) the pointer is taken relative to it.
 */
function eye(scene, x, y, k, depth, big = false, parent = null) {
    const pre = big ? 'eye_big_' : 'eye_';
    const ball = scene.add.image(x, y, key('crazy', pre + 'ball')).setScale(k);
    const iris = scene.add.image(x, y, key('crazy', pre + 'iris')).setScale(k);
    if (parent) parent.add([ball, iris]); else { ball.setDepth(depth); iris.setDepth(depth + 0.001); }
    const R = (big ? 34 : 20) * k * 0.45;
    let next = 1 + Math.random() * 4, blink = -1;
    const e = { ball, iris, k, x, y, alive: true };
    e.tick = (t) => {
        if (!ball.active) return;
        const p = scene.input.activePointer;
        const m = ball.getWorldTransformMatrix();
        const dx = p.x - m.tx, dy = p.y - m.ty, dd = Math.hypot(dx, dy) || 1;
        const r = Math.min(R, dd * 0.08);
        iris.setPosition(e.x + dx / dd * r, e.y + dy / dd * r * 0.8);
        if (blink < 0 && t > next) blink = t;
        let s = 1;
        if (blink >= 0) {
            const u = (t - blink) / 0.18;
            s = u < 0.5 ? 1 - u * 1.9 : u < 1 ? 0.05 + (u - 0.5) * 1.9 : 1;
            if (u >= 1) { blink = -1; next = t + 1.5 + Math.random() * 5; }
        }
        ball.setScale(e.k, e.k * s);
        iris.setScale(e.k, e.k * s);
        iris.setVisible(s > 0.25);
    };
    return e;
}

const crazy = {
    data: {
        accent: PINK, bg: 0x1a0614, onFill: ACIDG, onText: '#14081c', onIcon: 0x14081c,
        text: 0xffe6f2, dim: 0x6a4a5e, note: 0xd09ab8, rowBand: 0x3a0c2a, track: 0x5a2a4a, off: 0x7a4a6a,
        font: 'Rubik', head: 'Rubik Beastly', headBold: false, headScale: 0.7, labelPx: 20, rowPx: 16, smallSpacing: 2,
        thread: PINK, garden: [PINK, ACIDG, CYANC], glow: PINK, spore: ACIDG, basket: ACIDG, mycena: CYANC
    },
    myc: [0.18, 0.34],
    preload(scene) {
        loadFonts(scene, [['Rubik Beastly', 'RubikBeastly.ttf'], ['Rubik', 'Rubik.ttf', { weight: '300 900' }]]);
        loadImages(scene, 'crazy', ['band', 'band_wide', 'panel', 'rule', 'eye_ball', 'eye_iris', 'eye_big_ball', 'eye_big_iris',
            'plate0', 'plate1', 'plate2', 'plate3', 'plate4', 'title_upper', 'title_sub', ...[0, 2, 3, 4, 5, 6, 7, 8].map(i => 'title_' + i)]);
        if (!scene.cache.json.exists(key('crazy', 'layout'))) scene.load.json(key('crazy', 'layout'), DIR + 'crazy/layout.json');
    },
    rule(scene, K, x, h, left = false) {
        // the gum on the rule, the teeth biting into the painting (on a card's left edge: mirrored, biting outward)
        return cut(scene.add.image(left ? x - 23 : x - 3, 0, key('crazy', 'rule')).setOrigin(0, 0).setFlipX(left), h);
    },
    eyes(scene, list, RX, depth, parent, maxY = Infinity) {
        const eyes = list.filter(e => e.x < RX - 14 && e.y < maxY - 24).map(e => eye(scene, e.x, e.y, e.r / 20 * 1.15, depth, false, parent));
        onUpdate(scene, (t) => eyes.forEach(e => e.tick(t)));
    },
    band(scene, K, { RX, H, depth }) {
        const { name } = bandImage(scene, 'crazy', RX, H, depth);
        this.rule(scene, K, RX, H).setDepth(depth + 0.05);
        this.eyes(scene, scene.cache.json.get(key('crazy', 'layout'))[name], RX, depth + 0.03, null, H);
    },
    panelBg(scene, K, w, H) {
        const img = panelImage(scene, 'crazy', w, H);
        // the eyes go into the panel's body after it exists: MainScene's panel is a container that slides
        scene.time.delayedCall(0, () => {
            const body = img.parentContainer;
            if (!body) return;
            const before = body.list.length;
            this.eyes(scene, scene.cache.json.get(key('crazy', 'layout')).panel, w - 4, 0, body);
            body.list.slice(before).forEach((o, k) => body.moveTo(o, body.getIndex(img) + 1 + k));   // (ball, iris: in order)
        });
        return [img];
    },
    entry(scene, K, nav, { item, i, RX, y, ROW, garden, at }) {
        const PW = RX - 26, NAIL = -ROW / 2 - 7;
        const confetti = burst(scene, K, 'crazy', {
            speed: { min: 50, max: 190 }, angle: { min: 0, max: 360 }, lifespan: { min: 500, max: 1000 }, gravityY: 160,
            scale: { start: 1.6, end: 0.4 }, alpha: { start: 1, end: 0 }, tint: [PINK, ACIDG, CYANC, 0xffffff], rotate: { min: 0, max: 360 }
        });
        let swing, tag, letters, strings, peep, focused = false, enabled = true;
        const phase = i * 1.7;
        const h = K.navEntry(scene, nav, RX / 2, y, RX, ROW, {
            build: (c) => {
                swing = scene.add.container(0, NAIL);                          // it hangs from a nail: rotates round it
                tag = plate(scene, 'crazy', 'plate' + (i % 5), PW, ROW - 4, 14, 10).setPosition(0, -NAIL);
                strings = scene.add.graphics();
                strings.lineStyle(1.5, 0x14080e, 1).lineBetween(0, 0, -PW / 2 + 16, -NAIL - ROW / 2 + 6).lineBetween(0, 0, PW / 2 - 16, -NAIL - ROW / 2 + 6);
                strings.fillStyle(0x8a8a90, 1).fillCircle(0, 0, 2.5);
                // the label letter by letter, each its own ink, dancing
                const st = { fontFamily: 'Rubik Beastly', fontSize: '20px', color: INKS[0], padding: { x: 2, y: 4 } };
                letters = [...item.label].map((ch, j) => scene.add.text(0, 0, ch, { ...st, color: INKS[(j + i) % INKS.length] }).setOrigin(0.5));
                let total = letters.reduce((s, l) => s + l.width - 4, 0);
                if (total > PW - 30) letters.forEach(l => l.setFontSize(Math.floor(20 * (PW - 30) / total)));
                total = letters.reduce((s, l) => s + l.width - 4, 0);
                let lx = -total / 2;
                letters.forEach(l => { l.setData('x', lx + (l.width - 4) / 2); lx += l.width - 4; l.setPosition(l.getData('x'), -NAIL + 1); });
                swing.add([strings, tag, ...letters]);
                c.add(swing);
            },
            focus: (on) => {
                focused = on;
                scene.tweens.killTweensOf(swing);
                scene.tweens.add({ targets: swing, scale: on ? 1.06 : 1, duration: 160, ease: 'Back.easeOut' });
                if (on && !peep) {
                    // an eye pops out at the tag's end and stares at you
                    peep = eye(scene, PW / 2 - 8, -ROW / 2 + 2, 0, 0, false, h.container);
                    scene.tweens.add({ targets: peep, k: 0.6, duration: 280, ease: 'Back.easeOut' });
                } else if (!on && peep) {
                    const p = peep; peep = null;
                    scene.tweens.add({ targets: p, k: 0, duration: 140, ease: 'Sine.easeIn', onComplete: () => { p.ball.destroy(); p.iris.destroy(); } });
                }
            },
            press: () => {
                confetti.explode(26, RX / 2, y);
                scene.tweens.add({ targets: swing, scaleY: 0.85, scaleX: 1.12, duration: 70, yoyo: true });
                K.pulseDown(scene, RX, y, garden, at);
            },
            enable: (on) => { enabled = on; tag.setTint(on ? 0xffffff : 0x606060); letters.forEach(l => l.setAlpha(on ? 1 : 0.45)); },
            action: item.action
        });
        h.container.setDepth(K.DEPTH.ui);
        h.setEnabled(item.enabled !== false);
        onUpdate(scene, (t) => {
            if (!swing.active) return;
            const amp = focused ? 5 : 1.4, sp = focused ? 4.2 : 1.3;
            swing.angle = Math.sin(t * sp + phase) * amp;
            letters.forEach((l, j) => {
                const hop = focused ? Math.abs(Math.sin(t * 7 + j * 0.65)) * 5 : Math.sin(t * 2 + j * 0.9 + phase) * 1.2;
                l.y = -NAIL + 1 - hop;
                l.angle = focused ? Math.sin(t * 9 + j) * 8 : 0;
            });
            if (peep) peep.tick(t);
        });
        return { handle: h };
    },
    title(scene, K, x) {
        const d = K.DEPTH.title, lay = scene.cache.json.get(key('crazy', 'layout')).title;
        const CY = 74;
        scene.add.image(x, CY, K.softRect(scene, true)).setTint(0x14040e).setDisplaySize(lay.width + 140, 190).setAlpha(0.7).setDepth(d - 0.05);
        const pieces = [];
        let big = null;
        lay.letters.forEach((L, j) => {
            if (L.eye) { big = eye(scene, x + L.x, CY, 1, d + 0.02, true); return; }
            pieces.push({ img: scene.add.image(x + L.x, CY, key('crazy', L.file)).setDepth(d + 0.01), j, hop: 0 });
        });
        const up = scene.add.image(x - 120, 26, key('crazy', 'title_upper')).setDepth(d + 0.01);
        const sub = scene.add.image(x + 90, 128, key('crazy', 'title_sub')).setDepth(d + 0.01);
        // now and then a letter jumps
        const jump = () => {
            const p = pieces[Math.floor(Math.random() * pieces.length)];
            scene.tweens.add({ targets: p, hop: -16, duration: 180, yoyo: true, ease: 'Quad.easeOut' });
            scene.time.delayedCall(700 + Math.random() * 1800, jump);
        };
        scene.time.delayedCall(1200, jump);
        onUpdate(scene, (t) => {
            pieces.forEach(p => {
                p.img.angle = Math.sin(t * 1.7 + p.j * 1.3) * 4;
                p.img.y = CY + Math.sin(t * 2.3 + p.j) * 3 + p.hop;
            });
            up.angle = Math.sin(t * 2.1) * 3;
            sub.setScale(1 + Math.sin(t * 3) * 0.04, 1 - Math.sin(t * 3) * 0.04);
            big?.tick(t);
        });
    }
};

// =====================================================================================================================
// TRIPE: the tripe fungus (Auricularia mesenterica): wrinkled, rubbery, wet, its margins pale and hairy

const SALMON = 0xf0a080;
/** a jelly's wobble: squashed, then springing back */
function jiggle(scene, target, k = 1) {
    scene.tweens.killTweensOf(target);
    target.setScale(1 + 0.06 * k, 1 - 0.07 * k);
    scene.tweens.add({ targets: target, scaleX: 1, scaleY: 1, duration: 750, ease: 'Elastic.easeOut', easeParams: [1.2, 0.35] });
}
const tripe = {
    data: {
        accent: SALMON, bg: 0x150b0f, onFill: 0x4a2228, onText: '#ffd2c2', onIcon: 0xffc4b0,
        text: 0xece0da, dim: 0x6a5658, note: 0xb09a98, rowBand: 0x2a1a1e, track: 0x4a3438, off: 0x6a5458,
        font: 'Fraunces', head: 'Fraunces', headBold: true, headScale: 0.66, labelPx: 19, rowPx: 16, smallSpacing: 2,
        thread: SALMON, garden: [SALMON, 0xd8c8cc, 0xa07888], glow: SALMON, spore: 0xe8d8dc, basket: 0xc8607a, mycena: 0xd8c8cc
    },
    myc: false,
    preload(scene) {
        loadFonts(scene, [['Fraunces', 'Fraunces.ttf', { weight: '100 900' }]]);
        loadImages(scene, 'tripe', ['band', 'band_wide', 'panel', 'rule', 'title', 'title_sheen', ...[0, 1, 2, 3, 4].flatMap(i => ['plate' + i, `plate${i}_glow`])]);
        if (!scene.cache.json.exists(key('tripe', 'layout'))) scene.load.json(key('tripe', 'layout'), DIR + 'tripe/layout.json');
    },
    rule(scene, K, x, h, left = false) { return cut(scene.add.image(left ? x - 16 : x - 8, 0, key('tripe', 'rule')).setOrigin(0, 0).setFlipX(left), h); },
    band(scene, K, { RX, H, depth }) {
        bandImage(scene, 'tripe', RX, H, depth);
        this.rule(scene, K, RX, H).setDepth(depth + 0.05);
    },
    panelBg(scene, K, w, H) { return [panelImage(scene, 'tripe', w, H)]; },
    entry(scene, K, nav, ctx) {
        const drops = burst(scene, K, 'tripe', {
            speed: { min: 30, max: 110 }, angle: { min: 200, max: 340 }, lifespan: { min: 500, max: 900 }, gravityY: 300,
            scale: { start: 1.3, end: 0.7 }, alpha: { start: 0.9, end: 0.2 }, tint: [0xf2d6d0, SALMON, 0xc89890]
        });
        return plateEntry(scene, K, nav, ctx, {
            skin: 'tripe', plate: (i) => 'plate' + (i % 5), glow: (i) => `plate${i % 5}_glow`, glowColour: 0xfff0ea, side: 16, tb: 12,
            labelStyle: { fontFamily: 'Fraunces', fontStyle: 'bold', fontSize: '19px', color: '#2e1622' },
            labelColour: '#2e1622', labelOn: '#962e24', labelDim: '#8a7a84',
            // the pale lobes lifted off the dark wrinkles by a soft shadow
            build(P, under) {
                under.push(scene.add.image(2, 4, K.softRect(scene, true)).setTint(0x050203).setDisplaySize(P.PW + 26, P.ROW + 22).setAlpha(0.85));
            },
            // the wet sheen glistens
            glowPulse: (g) => scene.tweens.add({ targets: g, alpha: { from: 0.35, to: 1 }, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }),
            focus(P, on) { if (on) jiggle(scene, P.c, 0.6); },
            press(P) { jiggle(scene, P.c, 1.3); drops.explode(14, ctx.RX / 2, P.y + 4); }
        });
    },
    title(scene, K, x) {
        const d = K.DEPTH.title, Y = 6;
        // the letters breathe like a living jelly: cut into thin vertical strips, each swelling up from the baseline
        // a moment after its neighbour, so a slow soft wave rolls through the word (and the wet sheen with it)
        const src = scene.textures.get(key('tripe', 'title')).getSourceImage();
        const W = src.width, TH = src.height, x0 = x - W / 2, S = 6;
        const strips = [];
        for (let sx = 0; sx < W; sx += S) {
            // (exactly S wide: overlapping strips doubled the soft shadow into thin dark lines)
            const a = scene.add.image(x0, Y + TH, key('tripe', 'title')).setOrigin(0, 1).setCrop(sx, 0, S, TH).setDepth(d);
            const b = scene.add.image(x0, Y + TH, key('tripe', 'title_sheen')).setOrigin(0, 1).setCrop(sx, 0, S, TH)
                .setBlendMode(Phaser.BlendModes.ADD).setDepth(d + 0.01);
            strips.push({ a, b, ph: (sx + S / 2) * 0.011 });
        }
        onUpdate(scene, (t) => {
            const glint = 0.45 + 0.3 * Math.sin(t * 0.9);
            strips.forEach(({ a, b, ph }) => {
                const sy = 1 + 0.028 * Math.sin(t * 1.05 - ph) + 0.01 * Math.sin(t * 0.43 + ph * 2.3);
                const dy = 1.1 * Math.sin(t * 0.7 - ph * 0.6);
                a.setScale(1, sy).setY(Y + TH + dy);
                b.setScale(1, sy).setY(Y + TH + dy).setAlpha(glint + 0.25 * Math.sin(t * 1.3 - ph * 3));
            });
        });
        // and drip: a drop swells under a letter, stretches, falls
        const drips = scene.cache.json.get(key('tripe', 'layout')).drips;
        const drip = () => {
            const [dx, dy] = drips[Math.floor(Math.random() * drips.length)];
            const drop = scene.add.ellipse(x0 + dx, Y + dy - 1, 4, 3, 0xe8c4b8, 0.9).setDepth(d + 0.02);
            scene.tweens.chain({ targets: drop, tweens: [
                { scaleY: 2.2, y: Y + dy + 2, duration: 900, ease: 'Sine.easeIn' },
                { y: Y + dy + 70, scaleY: 1.4, alpha: 0, duration: 520, ease: 'Quad.easeIn' }
            ], onComplete: () => drop.destroy() });
            scene.time.delayedCall(1400 + Math.random() * 2600, drip);
        };
        scene.time.delayedCall(800, drip);
    }
};

// =====================================================================================================================
// PANELAK: a post-Soviet prefab tower at dusk, its windows lit now and then; a lattice girder for the rule; enamel
// signs; the name in rooftop letters, red neon, one of them broken

const AMBER = 0xffcc66, NEON = 0xff4a3a;
/** the facade's windows light up and go dark one by one; a TV flickers blue; the aviation light blinks */
function tenants(scene, layout, RX, depth, parent = null, maxY = Infinity) {
    const lit = parent ? 0.4 : 1, share = parent ? 0.18 : 0.3;      // (in a panel: fewer and dimmer, behind its text)
    const put = (o) => { if (parent) parent.add(o); else o.setDepth(depth); return o; };
    const wins = layout.windows.filter(([x, y, w, h]) => x + w <= RX - 2 && y + h <= maxY - 4).map(([x, y, w, h]) => {
        const kind = Math.random() < 0.15 ? 2 : Math.random() < 0.5 ? 1 : 0;
        const img = put(scene.add.image(x, y, key('panelak', 'win' + kind)).setOrigin(0).setCrop(0, 0, w, h)
            .setAlpha(Math.random() < share ? lit : 0));
        return { img, kind };
    });
    const toggle = () => {
        if (!wins.length) return;
        const w = wins[Math.floor(Math.random() * wins.length)];
        scene.tweens.add({ targets: w.img, alpha: w.img.alpha > 0.01 ? 0 : lit, duration: 160 });
        scene.time.delayedCall(700 + Math.random() * 2200, toggle);
    };
    scene.time.delayedCall(900, toggle);
    if (layout.aviation) {
        const [ax, ay] = layout.aviation;
        const halo = put(scene.add.image(ax, ay, 'mmGlow').setTint(NEON).setBlendMode(Phaser.BlendModes.ADD).setDisplaySize(22, 22));
        const dot = put(scene.add.circle(ax, ay, 2, 0xff6a5a));
        scene.tweens.add({ targets: [halo, dot], alpha: { from: 1, to: 0.08 }, duration: 260, hold: 500, repeatDelay: 900, yoyo: true, repeat: -1 });
    }
    onUpdate(scene, () => wins.forEach(w => {
        if (w.kind === 2 && w.img.alpha > 0.01 && w.img.active && !scene.tweens.isTweening(w.img)) w.img.setAlpha(lit * (0.75 + Math.random() * 0.25));
    }));
}
/**
 * An entry as a strip of glass blocks (luxfery) in a steel frame, like a stairwell's window: dark at night, its
 * label a neon tube, unlit. Focus = someone pressed the stairwell switch: the fluorescent tube behind the glass
 * strikes (blink, blink, on) and the label's neon lights up red; a click makes it buzz and sheds concrete dust.
 */
function luxferaEntry(scene, K, nav, { item, i, RX, y, ROW, garden, at }, dust) {
    const k = (n) => key('panelak', n);
    const PW = RX - 22, GW = PW - 16, GH = 40;
    const OFF = '#c4b4ae', ON = '#fff3ee', DIM = '#5e5a5c';
    let glassOff, glassOn, sw, swOn, label, fx, enabled = true;
    const h = K.navEntry(scene, nav, RX / 2, y, RX, ROW, {
        build: (c) => {
            glassOff = scene.add.tileSprite(0, 0, GW, GH, k('lux'));
            glassOn = scene.add.tileSprite(0, 0, GW, GH, k('lux_lit')).setAlpha(0);
            glassOff.tilePositionX = glassOn.tilePositionX = (i * 7) % 20;         // (not every strip cut at the same block)
            const chords = [-GH / 2 - 2, GH / 2 + 2].map(cy => scene.add.tileSprite(0, cy, PW, 6, k('girder')));
            const posts = [-1, 1].map(s => scene.add.image(s * (PW / 2 - 4), 0, k('post')));
            sw = scene.add.image(-PW / 2 + 4, 0, k('switch'));
            swOn = scene.add.image(-PW / 2 + 4, 0, k('switch_on')).setAlpha(0);
            label = scene.add.text(4, 0, item.label, { fontFamily: 'Jost', fontStyle: 'bold', fontSize: '18px', color: OFF,
                stroke: '#0c0d10', strokeThickness: 4, letterSpacing: 1, padding: { x: 14, y: 10 } }).setOrigin(0.5);
            for (let fs = 18; label.width - 28 > GW - 30 && fs > 11; fs--) label.setFontSize(fs - 1);
            fx = label.preFX?.addGlow(NEON, 0, 0, false, 0.1, 12);
            c.add([glassOff, glassOn, ...chords, ...posts, sw, swOn, label]);
        },
        focus: (on) => {
            scene.tweens.killTweensOf([glassOn, swOn, label]);
            if (fx) scene.tweens.killTweensOf(fx);
            if (on) {
                swOn.setAlpha(1);
                scene.tweens.chain({ targets: glassOn, tweens: [
                    { alpha: 0.6, duration: 40 }, { alpha: 0.05, duration: 110 }, { alpha: 0.75, duration: 40 },
                    { alpha: 0.15, duration: 140 }, { alpha: 0.85, duration: 80 }] });
                label.setColor(ON);
                if (fx) {
                    fx.outerStrength = 0;
                    scene.tweens.chain({ targets: fx, tweens: [{ outerStrength: 3.5, duration: 60, delay: 120 }, { outerStrength: 0.5, duration: 60 },
                        { outerStrength: 3.5, duration: 90 }, { outerStrength: { from: 3.5, to: 2.6 }, duration: 700, yoyo: true, repeat: -1 }] });
                }
            } else {
                swOn.setAlpha(0);
                scene.tweens.add({ targets: glassOn, alpha: 0, duration: 220 });
                label.setColor(enabled ? OFF : DIM);
                if (fx) fx.outerStrength = 0;
            }
        },
        press: () => {
            if (fx) scene.tweens.add({ targets: fx, outerStrength: 0.4, duration: 40, yoyo: true, repeat: 2 });   // the tube buzzes
            dust.explode(18, RX / 2, y + 12);
            K.pulseDown(scene, RX, y, garden, at);
        },
        enable: (on) => { enabled = on; glassOff.setTint(on ? 0xffffff : 0x6a6a6a); label.setColor(on ? OFF : DIM); sw.setAlpha(on ? 1 : 0.5); },
        action: item.action
    });
    h.container.setDepth(K.DEPTH.ui);
    h.setEnabled(item.enabled !== false);
    return { handle: h };
}

const panelak = {
    data: {
        accent: AMBER, bg: 0x111317, onFill: 0x1c3460, onText: '#ffe6a8', onIcon: AMBER,
        text: 0xe8e0cc, dim: 0x5a5e66, note: 0x9aa0aa, rowBand: 0x1e2430, track: 0x3a404a, off: 0x5a606a,
        font: 'Jost', head: 'Russo One', headBold: false, headScale: 0.66, labelPx: 19, rowPx: 16, smallSpacing: 3,
        thread: AMBER, garden: [AMBER, 0x9aa0aa, 0xff5a4a], glow: AMBER, spore: 0xd8dce4, basket: 0xff5a4a, mycena: AMBER
    },
    myc: false,
    preload(scene) {
        loadFonts(scene, [['Russo One', 'RussoOne.ttf'], ['Jost', 'Jost.ttf', { weight: '100 900' }]]);
        loadImages(scene, 'panelak', ['band', 'band_wide', 'panel', 'rule', 'win0', 'win1', 'win2', 'lux', 'lux_lit', 'girder', 'post',
            'switch', 'switch_on', 'title', 'title_neon', 'title_neon_broken', 'title_neon_upper', 'title_box_glow']);
        if (!scene.cache.json.exists(key('panelak', 'layout'))) scene.load.json(key('panelak', 'layout'), DIR + 'panelak/layout.json');
    },
    rule(scene, K, x, h) { return cut(scene.add.image(x + K.RULE / 2, 0, key('panelak', 'rule')).setOrigin(0.5, 0), h); },
    band(scene, K, { RX, H, depth }) {
        K.glowTex(scene);
        const { name } = bandImage(scene, 'panelak', RX, H, depth);
        tenants(scene, scene.cache.json.get(key('panelak', 'layout'))[name], RX, depth + 0.01, null, H);
        this.rule(scene, K, RX, H).setDepth(depth + 0.05);
    },
    panelBg(scene, K, w, H) {
        K.glowTex(scene);
        const img = panelImage(scene, 'panelak', w, H);
        scene.time.delayedCall(0, () => {
            const body = img.parentContainer;
            if (!body) return;
            const before = body.list.length;
            tenants(scene, scene.cache.json.get(key('panelak', 'layout')).panel, w - 4, 0, body);
            body.list.slice(before).forEach((o, k) => body.moveTo(o, body.getIndex(img) + 1 + k));
        });
        return [img];
    },
    entry(scene, K, nav, ctx) {
        const dust = burst(scene, K, 'panelak', {
            speed: { min: 10, max: 60 }, angle: { min: 0, max: 360 }, lifespan: { min: 600, max: 1100 }, gravityY: 90,
            scale: { start: 1.2, end: 0.4 }, alpha: { start: 0.8, end: 0 }, tint: [0xb8bcc4, 0x8a8e96, 0xd8d4c8]
        });
        return luxferaEntry(scene, K, nav, ctx, dust);
    },
    title(scene, K, x) {
        const d = K.DEPTH.title, Y = 6;
        K.glowTex(scene);
        const img = scene.add.image(x, Y, key('panelak', 'title')).setOrigin(0.5, 0).setDepth(d);
        scene.add.image(x, 70, K.softRect(scene, true)).setTint(0x08090c).setDisplaySize(img.width + 60, 170).setAlpha(0.55).setDepth(d - 0.05);
        const neon = scene.add.image(x, Y, key('panelak', 'title_neon')).setOrigin(0.5, 0).setBlendMode(Phaser.BlendModes.ADD).setDepth(d + 0.01);
        const broken = scene.add.image(x, Y, key('panelak', 'title_neon_broken')).setOrigin(0.5, 0).setBlendMode(Phaser.BlendModes.ADD).setDepth(d + 0.01);
        // UPPER in cold white neon, steady; the shop sign under it backlit, its fluorescent tube humming
        const upper = scene.add.image(x, Y, key('panelak', 'title_neon_upper')).setOrigin(0.5, 0).setBlendMode(Phaser.BlendModes.ADD).setDepth(d + 0.01);
        const box = scene.add.image(x, Y, key('panelak', 'title_box_glow')).setOrigin(0.5, 0).setBlendMode(Phaser.BlendModes.ADD).setDepth(d + 0.01);
        // the neon hums; the broken letter sputters: on for a while, then it fails and catches again
        let state = 1, until = 2;
        onUpdate(scene, (t) => {
            neon.setAlpha(0.88 + Math.sin(t * 50) * 0.04 + Math.random() * 0.06);
            upper.setAlpha(0.9 + Math.random() * 0.1);
            box.setAlpha(0.55 + Math.sin(t * 2) * 0.05 + (Math.random() < 0.01 ? -0.3 : 0));
            if (t > until) { state = state ? 0 : 1; until = t + (state ? 1 + Math.random() * 4 : 0.15 + Math.random() * 1.2); }
            broken.setAlpha(state ? 0.85 + Math.random() * 0.15 : (Math.random() < 0.12 ? 0.7 : 0.04));
        });
        const [ax, ay] = scene.cache.json.get(key('panelak', 'layout')).title.aviation;
        const ox = x - img.width / 2;
        const halo = scene.add.image(ox + ax, Y + ay, K.glowTex(scene)).setTint(NEON).setBlendMode(Phaser.BlendModes.ADD).setDisplaySize(26, 26).setDepth(d + 0.02);
        const dot = scene.add.circle(ox + ax, Y + ay, 2.2, 0xff7a6a).setDepth(d + 0.02);
        scene.tweens.add({ targets: [halo, dot], alpha: { from: 1, to: 0.08 }, duration: 260, hold: 500, repeatDelay: 900, yoyo: true, repeat: -1 });
    }
};

export const SKINS = { rust, biomech, jungle, crazy, tripe, panelak };
