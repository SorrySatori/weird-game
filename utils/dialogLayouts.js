/**
 * dialogLayouts.js — the game's dialogue presentation ("chronicle" layout).
 *
 * A scrollable narration log + a name/portrait plate, with numbered response lines along the
 * bottom. The character portrait reuses the speaker's own sprite already loaded in the scene
 * (shown static, first frame).
 *
 * The LOGIC stays in GameScene: showDialog resolves/translates content, runs onTrigger, then hands
 * a normalized model to renderDialogLayout(). Options carry their own `activate()` (the real
 * navigation). This module only builds GameObjects + wires hover/click → commit(activate).
 *
 * Model shape (built by GameScene._buildDialogModel):
 *   { speaker: string|null, text: string,
 *     options: [{ label: string, used: boolean, isClose: boolean, activate: fn }] }
 *
 * Everything created goes into scene.dialogBox (a container destroyed by hideDialog); masks go into
 * scene._dialogMasks and wheel handlers into scene._dialogWheel (also cleaned there).
 */

/** Entry point called by showDialog to render a dialog from its normalized model. */
export function renderDialogLayout(scene, model) {
    RENDERERS.chronicle(scene, model);
}

// ------------------------------------------------------------------ shared helpers

/** Play the murmur and run the option's navigation. */
function commit(scene, activate) {
    try { scene.dialogMurmur?.play?.({ volume: 0.8, rate: 0.9 }); } catch (e) { /* ignore */ }
    activate();
}

/** Mask `target` to a screen rect and let the wheel scroll it vertically when it overflows. */
function attachScroll(scene, target, contentHeight, view) {
    if (contentHeight <= view.h) return;      // fits — no scroll needed
    const g = scene.add.graphics();
    g.fillStyle(0xffffff);
    g.fillRect(view.x, view.y, view.w, view.h);
    target.setMask(new Phaser.Display.Masks.GeometryMask(scene, g));
    (scene._dialogMasks = scene._dialogMasks || []).push(g);

    const topY = target.y;
    const minY = topY - (contentHeight - view.h);
    const step = amt => { target.y = Phaser.Math.Clamp(target.y + amt, minY, topY); };

    const handler = (pointer, objs, dx, dy) => {
        if (!scene.dialogVisible) return;
        if (pointer.x < view.x || pointer.x > view.x + view.w || pointer.y < view.y || pointer.y > view.y + view.h) return;
        step(dy > 0 ? -28 : 28);
    };
    scene.input.on('wheel', handler);
    (scene._dialogWheel = scene._dialogWheel || []).push(handler);

    // Visible ▲/▼ affordance at the view's right edge (also click-to-scroll), so it's obvious the
    // panel scrolls and it works without a wheel. Added to the dialog box (destroyed with it).
    const ac = view.arrowColor || '#8fb7a0';
    const mkArrow = (glyph, ay) => {
        const a = scene.add.text(view.x + view.w - 10, ay, glyph, { fontSize: '16px', fill: ac }).setOrigin(0.5);
        a.setInteractive({ useHandCursor: true });
        a.on('pointerover', () => a.setAlpha(1));
        a.on('pointerout', () => a.setAlpha(0.75));
        a.on('pointerdown', () => step(glyph === '▲' ? 60 : -60));
        a.setAlpha(0.75);
        scene.dialogBox.add(a);
        return a;
    };
    mkArrow('▲', view.y + 10);
    mkArrow('▼', view.y + view.h - 10);
}

/**
 * A clickable option row. Returns its pixel height.
 * opts: { font, size, color, hover, usedColor, prefix, align:'left'|'center', wrapW, accent:0xRRGGBB|null }
 */
function optionRow(scene, parent, x, y, opt, opts, index) {
    const baseColor = opt.isClose ? (opts.closeColor || opts.color) : (opt.used ? opts.usedColor : opts.color);
    const prefix = typeof opts.prefix === 'function' ? opts.prefix(index, opt) : (opts.prefix || '');
    const label = scene.add.text(x, y, prefix + opt.label, {
        fontFamily: opts.font, fontSize: opts.size, fill: baseColor,
        wordWrap: { width: opts.wrapW }, align: opts.align || 'left',
    });
    if (opts.align === 'center') label.setOrigin(0.5, 0); else label.setOrigin(0, 0);
    parent.add(label);

    const h = label.height;
    // Hit area / hover accent spanning the row.
    const hitW = opts.hitW || (opts.wrapW + 24);
    const hitX = opts.align === 'center' ? x - hitW / 2 : x - 8;
    const hit = scene.add.rectangle(hitX, y - 4, hitW, h + 8, 0xffffff, 0.001).setOrigin(0, 0);
    hit.setInteractive({ useHandCursor: true });
    parent.add(hit);

    let accent = null;
    if (opts.accent != null) {
        accent = scene.add.rectangle(hitX, y - 4, 3, h + 8, opts.accent, 0).setOrigin(0, 0);
        parent.add(accent);
    }

    hit.on('pointerover', () => {
        label.setFill(opts.hover);
        if (accent) accent.setAlpha(1);
        if (opts.hoverBg) hit.setFillStyle(opts.hoverBg, 0.18);
    });
    hit.on('pointerout', () => {
        label.setFill(baseColor);
        if (accent) accent.setAlpha(0);
        if (opts.hoverBg) hit.setFillStyle(0xffffff, 0.001);
    });
    hit.on('pointerdown', () => { hit.disableInteractive(); commit(scene, opt.activate); });

    return h + (opts.gap != null ? opts.gap : 12);
}

/** New empty dialog container at the top depth. */
function newBox(scene) {
    const box = scene.add.container(0, 0).setDepth(1000);
    scene.dialogBox = box;
    return box;
}

/**
 * Best-effort portrait texture for a speaker, using assets ALREADY loaded in the scene — no
 * per-NPC wiring needed. A scene may override precisely via `scene.dialogPortraits = { 'Gnur': 'gnur' }`.
 * Matching: exact normalized key first (e.g. "Gnur" → 'gnur'), then a substring match on the
 * speaker's words (e.g. "Fungal Master Thaal" → 'fungal_master'); obvious non-character keys skipped.
 */
function resolvePortraitTexture(scene, speaker) {
    if (!speaker) return null;
    const override = scene.dialogPortraits && scene.dialogPortraits[speaker];
    if (override && scene.textures.exists(override)) return override;

    // Normalize: strip accents (Torchère → torchere), lowercase, drop non-alphanumerics.
    const norm = s => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
    const spk = norm(speaker);
    if (spk.length < 3) return null;
    const words = String(speaker).split(/[^A-Za-zÀ-ÿ0-9]+/).map(norm).filter(w => w.length >= 3);
    const cands = [...new Set([spk, ...words])];
    const SKIP = /(^|_)(bg|background|ground|arrow|door|ui|panel|button|icon|logo|shadow|spore|map|title|cursor|frame|glow|mist|bar)($|_)|^cs_/;
    const keys = scene.textures.getTextureKeys().filter(k => !SKIP.test(k.toLowerCase()));

    // Pass 1: whole-key normalized equality (e.g. "Gnur" → 'gnur').
    for (const k of keys) { if (cands.includes(norm(k))) return k; }
    // Pass 2: a WORD-PART of the key matches a candidate (e.g. 'lamp_don' → 'don', 'fungal_master' → 'master').
    for (const k of keys) {
        const parts = k.split(/[^A-Za-z0-9]+/).map(norm).filter(p => p.length >= 3);
        if (parts.some(p => cands.includes(p))) return k;
    }
    // Pass 3: loose substring either way (handles "fungal_master" ⊂ "fungalmasterthaal").
    for (const k of keys) {
        const kn = norm(k); if (kn.length < 4) continue;
        for (const c of cands) { if (c.length >= 4 && (kn.includes(c) || c.includes(kn))) return k; }
    }
    return null;
}

/** Portrait plate: the scene's own character sprite (head-aligned, cropped) + a name strip. */
function addPortrait(scene, parent, cx, cy, w, h, key, name, opts) {
    parent.add(scene.add.rectangle(cx, cy, w, h, 0x0a1a12, 0.9).setStrokeStyle(1, 0x2f5a44));
    const innerW = w - 12, innerH = h - 12;
    if (key && scene.textures.exists(key)) {
        const spr = scene.add.sprite(cx, cy, key);            // add.sprite → frame 0 for spritesheets
        spr.setScale(innerW / spr.width);
        spr.y = cy - h / 2 + 6 + spr.displayHeight / 2;        // top-align so the head shows
        parent.add(spr);
        const g = scene.add.graphics();
        g.fillStyle(0xffffff);
        g.fillRect(cx - innerW / 2, cy - innerH / 2, innerW, innerH);
        spr.setMask(new Phaser.Display.Masks.GeometryMask(scene, g));
        (scene._dialogMasks = scene._dialogMasks || []).push(g);
        // Static portrait: frame 0 of the sprite (spritesheets default to their first frame).
        if (spr.anims) spr.anims.stop();
    } else {
        parent.add(scene.add.text(cx, cy - 20, '▓▓', { fontFamily: opts.font, fontSize: '40px', fill: '#274' }).setOrigin(0.5));
    }
    parent.add(scene.add.rectangle(cx, cy + h / 2 - 16, w, 32, 0x000000, 0.55));
    parent.add(scene.add.text(cx, cy + h / 2 - 16, name || '—', {
        fontFamily: opts.font, fontSize: '14px', fill: opts.nameColor, align: 'center',
        wordWrap: { width: w - 10 }, fontStyle: 'bold',
    }).setOrigin(0.5));
}

// ------------------------------------------------------------------ layout renderers

const RENDERERS = {
    // ---- CHRONICLE: narration log (left) + name/portrait plate (right) + numbered lines (bottom)
    chronicle(scene, model) {
        const box = newBox(scene);
        const INK = '#c8e6d0', DIM = '#5f7a68', HL = '#ffffff', NAME = '#e8c46a', FONT = '"Courier New", monospace';
        // The dialog is laid out 800 wide; centre it on the actual canvas. `dx` shifts the 800-design.
        const CX = Math.round(scene.scale.width / 2), dx = CX - 400;

        box.add(scene.add.rectangle(CX, 300, scene.scale.width, 600, 0x05080a, 0.82));  // dim the world
        const panel = scene.add.rectangle(CX, 300, 720, 520, 0x0c1410, 0.97).setStrokeStyle(2, 0x2f5a44);
        box.add(panel);

        // Name / portrait plate, top-right — a static portrait from the speaker's own scene sprite.
        addPortrait(scene, box, 650 + dx, 150, 150, 170, resolvePortraitTexture(scene, model.speaker), model.speaker, { font: FONT, nameColor: NAME });

        // A thin rule under the log region, separating narration from responses.
        box.add(scene.add.rectangle(CX, 392, 660, 1, 0x2f5a44, 0.7));

        // Narration log, left.
        const view = { x: 70 + dx, y: 82, w: 486, h: 296, arrowColor: NAME };
        const logC = scene.add.container(view.x, view.y);
        box.add(logC);
        const speakerLine = model.speaker
            ? scene.add.text(0, 0, model.speaker + ':', { fontFamily: FONT, fontSize: '19px', fill: NAME, fontStyle: 'bold' })
            : null;
        if (speakerLine) logC.add(speakerLine);
        const body = scene.add.text(0, speakerLine ? 34 : 0, model.text, {
            fontFamily: FONT, fontSize: '18px', fill: INK, wordWrap: { width: view.w - 14 }, lineSpacing: 9,
        });
        logC.add(body);
        attachScroll(scene, logC, (speakerLine ? 34 : 0) + body.height, view);

        // Numbered response lines, bottom (their own scroll area if long).
        const oview = { x: 70 + dx, y: 410, w: 660, h: 148, arrowColor: NAME };
        const optsC = scene.add.container(oview.x, oview.y);
        box.add(optsC);
        let y = 0;
        model.options.forEach((opt, i) => {
            y += optionRow(scene, optsC, 0, y, opt, {
                font: FONT, size: '18px', color: opt.isClose ? DIM : INK, usedColor: DIM, hover: HL,
                prefix: (idx) => `${idx + 1}. `, align: 'left', wrapW: oview.w - 40, gap: 11,
            }, i);
        });
        attachScroll(scene, optsC, y, oview);
    },

};
