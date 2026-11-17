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

import { UI_FONT, UI_SIZE } from './pixelFrame.js';

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
    const g = scene.make.graphics({}, false); // a mask shape only: off the display list, so it never shows as a white box
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
 * per-NPC wiring needed. A scene may override precisely via `scene.dialogPortraits = { 'Gnur': 'gnur' }`,
 * or point at one frame of a sheet with `{ key, frame }` (shown whole, integer-scaled — e.g. the symbionts), or
 * `{ key, frame, zoom, top }` for a bust of a full-figure sheet (integer zoom, frame row `top` at the plate's top).
 * Matching: exact normalized key first (e.g. "Gnur" → 'gnur'), then a substring match on the
 * speaker's words (e.g. "Fungal Master Thaal" → 'fungal_master'); obvious non-character keys skipped.
 */
function resolvePortraitTexture(scene, speaker) {
    if (!speaker) return null;
    const override = scene.dialogPortraits && scene.dialogPortraits[speaker];
    if (override && scene.textures.exists(override.key ?? override)) return override;

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
    // the menu kit's nine-slice card at the 2x grid (as the shop and the journal), its frame ~10 px thick
    parent.add(scene.add.nineslice(cx, cy, 'menuCard', 0, w / 2, h / 2, 7, 7, 7, 7).setScale(2));
    const innerW = w - 20, innerH = h - 20;
    if (key && key.key && key.zoom && scene.textures.exists(key.key)) {
        // A bust from one frame of a full-figure pixel-art sheet: integer zoom, the frame's row `top` (the top of the
        // head) at the plate's top edge, the rest masked off. zoom 2 puts the bust on the UI layer's 2x grid.
        const spr = scene.add.sprite(cx, cy - innerH / 2 + 4 - (key.top || 0) * key.zoom, key.key, key.frame ?? 0)
            .setOrigin(0.5, 0).setScale(key.zoom);
        parent.add(spr);
        const g = scene.make.graphics({}, false); // a mask shape only: off the display list, so it never shows as a white box
        g.fillStyle(0xffffff);
        g.fillRect(cx - innerW / 2, cy - innerH / 2, innerW, innerH);
        spr.setMask(new Phaser.Display.Masks.GeometryMask(scene, g));
        (scene._dialogMasks = scene._dialogMasks || []).push(g);
    } else if (key && key.key && scene.textures.exists(key.key)) {
        // One frame of a sheet (a small pixel-art sprite): whole, integer-scaled, centred above the name strip.
        const spr = scene.add.sprite(cx, cy - 16, key.key, key.frame);
        spr.setScale(Math.max(1, Math.floor(Math.min(innerW, innerH - 32) / Math.max(spr.width, spr.height))));
        parent.add(spr);
    } else if (key && scene.textures.exists(key)) {
        const spr = scene.add.sprite(cx, cy, key);            // add.sprite → frame 0 for spritesheets
        // a sprite zooms by whole steps (its pixels stay even); a picture bigger than the plate (a place's background
        // as its "portrait") shrinks to fit, as a thumbnail
        const fit = innerW / spr.width;
        spr.setScale(fit >= 1 ? Math.floor(fit) : fit);
        spr.y = cy - h / 2 + 10 + spr.displayHeight / 2;       // top-align so the head shows
        parent.add(spr);
        const g = scene.make.graphics({}, false); // a mask shape only: off the display list, so it never shows as a white box
        g.fillStyle(0xffffff);
        g.fillRect(cx - innerW / 2, cy - innerH / 2, innerW, innerH);
        spr.setMask(new Phaser.Display.Masks.GeometryMask(scene, g));
        (scene._dialogMasks = scene._dialogMasks || []).push(g);
        // Static portrait: frame 0 of the sprite (spritesheets default to their first frame).
        if (spr.anims) spr.anims.stop();
    }
    // (no name strip under the bust: the log's first line names the speaker, and a long name won't fit the plate)
}

// ------------------------------------------------------------------ layout renderers

const RENDERERS = {
    // ---- CHRONICLE: narration log (left) + name/portrait plate (right) + numbered lines (bottom)
    chronicle(scene, model) {
        const box = newBox(scene);
        const INK = '#c8e6d0', DIM = '#5f7a68', HL = '#ffffff', NAME = '#e8c46a', FONT = UI_FONT;
        // Centred on the canvas, 920 wide: the pixel font (22 px, monospace) needs the room for ~50 characters a line
        const CX = Math.round(scene.scale.width / 2), PW = 920, left = CX - PW / 2;

        box.add(scene.add.rectangle(CX, 300, scene.scale.width, 600, 0x05080a, 0.82));  // dim the world
        // the menu kit's nine-slice card at the 2x grid, as the shop and the journal (CX is even: the edges sit on the grid)
        const panel = scene.add.nineslice(CX, 300, 'menuCard', 0, PW / 2, 520 / 2, 7, 7, 7, 7).setScale(2);
        box.add(panel);

        // Portrait plate, top-right: a static bust from the speaker's own scene sprite (none for a speakerless line)
        const portrait = resolvePortraitTexture(scene, model.speaker) || resolvePortraitTexture(scene, model.speakerEn);
        const PLATE_W = 152, plateX = left + PW - 30 - PLATE_W / 2;
        if (portrait) addPortrait(scene, box, plateX, 140, PLATE_W, 152, portrait, model.speaker, { font: FONT, nameColor: NAME });

        // Numbered response lines at the bottom, built first: they take the room they need (up to OPT_MAX, then they
        // scroll) and the narration log above gets the rest, so five options don't scroll while the log sits half empty
        const BOTTOM = 548, OPT_MAX = 236;
        const optsC = scene.add.container(left + 30, 0);
        box.add(optsC);
        let y = 0;
        model.options.forEach((opt, i) => {
            y += optionRow(scene, optsC, 0, y, opt, {
                font: FONT, size: UI_SIZE, color: opt.isClose ? DIM : INK, usedColor: DIM, hover: HL,
                prefix: (idx) => `${idx + 1}. `, align: 'left', wrapW: PW - 100, gap: 6,
            }, i);
        });
        const optH = Math.min(OPT_MAX, Math.max(y, 120));
        const oview = { x: left + 30, y: Math.round((BOTTOM - optH) / 2) * 2, w: PW - 60, h: optH, arrowColor: NAME };
        optsC.y = oview.y;
        attachScroll(scene, optsC, y, oview);

        // A thin rule between the narration and the responses
        box.add(scene.add.rectangle(CX, oview.y - 14, PW - 60, 2, 0x8a6a2a, 0.7));     // 2 px: one grid pixel

        // Narration log, top-left, down to the rule
        const top = 70;
        const view = { x: left + 30, y: top, w: (portrait ? plateX - PLATE_W / 2 - 20 : left + PW - 30) - (left + 30), h: oview.y - 28 - top, arrowColor: NAME };
        const logC = scene.add.container(view.x, view.y);
        box.add(logC);
        const speakerLine = model.speaker
            ? scene.add.text(0, 0, model.speaker + ':', { fontFamily: FONT, fontSize: UI_SIZE, fill: NAME })
            : null;
        if (speakerLine) logC.add(speakerLine);
        const body = scene.add.text(0, speakerLine ? 34 : 0, model.text, {
            fontFamily: FONT, fontSize: UI_SIZE, fill: INK, wordWrap: { width: view.w - 14 }, lineSpacing: 6,
        });
        logC.add(body);
        attachScroll(scene, logC, (speakerLine ? 34 : 0) + body.height, view);
    },

};
