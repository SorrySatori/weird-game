/**
 * dialogLayouts.js: the entry point of the dialogue presentation and the helpers its styles share.
 *
 * The player picks the style in Settings (utils/dialogStyles.js draws them):
 *   bubbles  in the world: the line in a plate over the speaker, the replies in a plate over the protagonist
 *   cinema   letterbox bars, the line as a subtitle in the bottom bar with the speaker's portrait, the replies on the right
 *
 * The LOGIC stays in GameScene: showDialog resolves/translates content, runs onTrigger, then hands
 * a normalized model to renderDialogLayout(). Options carry their own `activate()` (the real
 * navigation). The styles only build GameObjects + wire hover/click → commit(activate).
 *
 * Model shape (built by GameScene._buildDialogModel):
 *   { speaker: string|null, speakerEn: string|null, text: string,
 *     options: [{ label: string, used: boolean, isClose: boolean, activate: fn }] }
 *
 * Everything created goes into scene.dialogBox (a container destroyed by hideDialog); masks go into
 * scene._dialogMasks and wheel handlers into scene._dialogWheel (also cleaned there).
 */

import { getSetting, setSetting } from '../systems/GameSettings.js';
import { STYLE_RENDERERS } from './dialogStyles.js';
import { startTalk, stopTalk } from './talk.js';

/** The presentations the player can pick in Settings; the first is the default, and an unknown saved value (an older
 * trial style) falls back to it. */
export const DIALOG_STYLES = ['bubbles', 'cinema'];
export const currentDialogStyle = () => (DIALOG_STYLES.includes(getSetting('dialogStyle')) ? getSetting('dialogStyle') : DIALOG_STYLES[0]);

/**
 * Entry point called by showDialog to render a dialog from its normalized model.
 * The conversation so far (the lines and the replies picked) is kept in scene._dialogLog until the dialog closes, for
 * the styles that show a transcript; `replay` re-renders the current line (another style) without logging it again.
 */
export function renderDialogLayout(scene, model, { replay = false } = {}) {
    if (!replay) {
        const log = scene._dialogLog || (scene._dialogLog = []);
        model.fresh = log.length === 0;
        log.push({ speaker: model.speaker, text: model.text });
        if (log.length > 16) log.splice(0, log.length - 16);
    } else {
        model.fresh = false;
    }
    scene._dialogModel = model;
    STYLE_RENDERERS[currentDialogStyle()](scene, model);
    scene.onDialogLayout?.(currentDialogStyle());   // a scene that frames its shot per style (the bus)
    // the speaker's mouth moves for the new line (the style lists the sprites: in the world, the portrait)
    if (replay) stopTalk(scene); else startTalk(scene, scene._dialogSpeakers, model.text, `${model.speaker || ''} ${model.speakerEn || ''}`);
}

/** Next (dir 1) or previous style; an open dialog is re-drawn in it at once. Returns the new style. */
export function cycleDialogStyle(scene, dir = 1) {
    const n = DIALOG_STYLES.length;
    const next = DIALOG_STYLES[(DIALOG_STYLES.indexOf(currentDialogStyle()) + dir + n) % n];
    setSetting('dialogStyle', next);
    if (scene?.dialogVisible && scene._dialogModel) {
        scene.dialogBox?.destroy();
        scene.dialogBox = null;
        scene.clearDialogLayoutArtifacts();
        renderDialogLayout(scene, scene._dialogModel, { replay: true });
        scene.restackNotices?.();
    }
    return next;
}

// ------------------------------------------------------------------ shared helpers

/** Play the murmur, log the reply (the transcript styles show it) and run the option's navigation. */
export function commit(scene, opt) {
    try { scene.dialogMurmur?.play?.({ volume: 0.8, rate: 0.9 }); } catch (e) { /* ignore */ }
    if (!opt.isClose && scene._dialogLog) scene._dialogLog.push({ reply: opt.label });
    opt.activate();
}

/**
 * Mask `target` to a screen rect and let the wheel scroll it vertically when it overflows.
 * view: { x, y, w, h, arrowColor?, startAtEnd? (show the end first: a transcript), arrows? (false: none) }
 * Returns true when it scrolls.
 */
export function attachScroll(scene, target, contentHeight, view) {
    if (contentHeight <= view.h) return false;   // fits — no scroll needed
    const g = scene.make.graphics({}, false).setScrollFactor(0); // a mask shape only: off the display list, so it never shows as a white box
    g.fillStyle(0xffffff);
    g.fillRect(view.x, view.y, view.w, view.h);
    target.setMask(new Phaser.Display.Masks.GeometryMask(scene, g));
    (scene._dialogMasks = scene._dialogMasks || []).push(g);

    const topY = target.y;
    const minY = topY - (contentHeight - view.h);
    const step = amt => { target.y = Math.round(Phaser.Math.Clamp(target.y + amt, minY, topY) / 2) * 2; };
    if (view.startAtEnd) step(-contentHeight);

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
    if (view.arrows === false) return true;
    mkArrow('▲', view.y + 10);
    mkArrow('▼', view.y + view.h - 10);
    return true;
}

/**
 * A line too long for its view, read in pages instead of scrolled (the user's idea, 2026-11-27: a page at a time reads
 * calmer than a scrolling text). The text is cut into pages that end where a sentence does (a sentence longer than a page
 * by lines); a page that has more after it ends in a
 * blinking "..." (click it or anywhere on the text: the next page), ▲/▼ at the view's right edge turn back and forth (the
 * unavailable one dimmed),
 * the wheel over the text turns pages too. When paging, the text wraps a little narrower so the dots always fit after
 * the page's last line; the view (the plate, the bar) keeps its size.
 * view: { x, y, w, h, wrap, lineSpacing?, color? (the dots and arrows) }. Returns true when it pages.
 */
export function attachPages(scene, body, view) {
    if (body.height <= view.h) return false;   // fits: one page
    const ls = view.lineSpacing ?? 4;
    const DOTS = '...', color = view.color || '#e8c46a';
    const font = { fontFamily: body.style.fontFamily, fontSize: body.style.fontSize };
    const probe = scene.add.text(0, 0, DOTS, font).setVisible(false);
    const dotsW = Math.ceil(probe.width) + 10;
    body.setWordWrapWidth(view.wrap - dotsW);
    const full = body.text;
    const lines = body.getWrappedText();
    const step = (body.height + ls) / Math.max(1, lines.length);
    const per = Math.max(1, Math.floor((view.h + ls) / step));
    const count = t => body.getWrappedText(t).length;
    // pages end where a sentence does (a page reads as a whole); a sentence longer than a page is cut by lines
    const pages = [];
    let cur = '';
    const flush = () => { if (cur.trim()) pages.push(cur.trim()); cur = ''; };
    const sentences = full.match(/[^.!?…\n]*(?:[.!?…]+["“”'‘’)\]]*|\n+|$)\s*/g).filter(t => t.length);
    for (const sen of sentences) {
        const cand = cur + sen;
        if (count(cand.trim()) <= per) { cur = cand; continue; }
        flush();
        if (count(sen.trim()) <= per) { cur = sen.replace(/^\s+/, ''); continue; }
        const ln = body.getWrappedText(sen.trim());                      // too long for one page: by lines
        for (let i = 0; i < ln.length; i += per) {
            const part = ln.slice(i, i + per).join(' ');
            if (i + per < ln.length) pages.push(part.trim()); else cur = part + ' ';
        }
    }
    flush();
    if (pages.length < 2) { probe.destroy(); body.setWordWrapWidth(view.wrap); return false; }

    const parent = body.parentContainer || scene.dialogBox;
    const dots = scene.add.text(0, 0, DOTS, { ...font, fill: color }).setInteractive({ useHandCursor: true });
    parent.add(dots);
    const blink = scene.tweens.add({ targets: dots, alpha: { from: 1, to: 0.35 }, duration: 650, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    dots.once('destroy', () => blink.remove());
    const arrow = (glyph, ay) => {
        const a = scene.add.text(view.x + view.w - 10, ay, glyph, { fontSize: '16px', fill: color }).setOrigin(0.5);
        a.setInteractive({ useHandCursor: true });
        a.on('pointerover', () => { if (a.input?.enabled) a.setAlpha(1); });
        a.on('pointerout', () => { if (a.input?.enabled) a.setAlpha(0.75); });
        parent.add(a);
        return a;
    };
    const up = arrow('▲', view.y + 10), down = arrow('▼', view.y + view.h - 10);

    let page = 0;
    const show = i => {
        page = Phaser.Math.Clamp(i, 0, pages.length - 1);
        body.setText(pages[page]);
        const more = page < pages.length - 1;
        dots.setVisible(more);
        if (more) {
            const ln = body.getWrappedText();
            probe.setText(ln[ln.length - 1].trimEnd());
            dots.setPosition(Math.round((body.x + probe.width + 12) / 2) * 2, body.y + Math.round((ln.length - 1) * step));
        }
        for (const [a, on] of [[up, page > 0], [down, more]]) {
            if (on) a.setInteractive({ useHandCursor: true }).setAlpha(0.75);
            else a.disableInteractive().setAlpha(0.25);
        }
        if (more) body.setInteractive({ useHandCursor: true }); else body.disableInteractive();   // (its new size)
    };
    dots.on('pointerdown', () => show(page + 1));
    body.on('pointerdown', () => show(page + 1));                    // a click anywhere on the text turns the page too
    up.on('pointerdown', () => show(page - 1));
    down.on('pointerdown', () => show(page + 1));
    const handler = (pointer, objs, dx, dy) => {
        if (!scene.dialogVisible) return;
        if (pointer.x < view.x || pointer.x > view.x + view.w || pointer.y < view.y || pointer.y > view.y + view.h) return;
        show(page + (dy > 0 ? 1 : -1));
    };
    scene.input.on('wheel', handler);
    (scene._dialogWheel = scene._dialogWheel || []).push(handler);
    body.once('destroy', () => probe.destroy());
    scene._dialogPages = { count: pages.length, show, get page() { return page; } };   // (tests)
    show(0);
    return true;
}

/** New empty dialog container at the top depth. */
export function newBox(scene) {
    // pinned to the screen, so a scene can move its camera under an open dialog (the bus frames the Bishop above the
    // Cinema bar)
    const box = scene.add.container(0, 0).setDepth(1000).setScrollFactor(0);
    scene.dialogBox = box;
    scene._noticeSpot = null;    // where the notices go while it's open: the style sets these (GameScene.restackNotices)
    scene._noticeAvoid = null;
    scene._dialogSpeakers = [];  // the speaker's sprites whose mouth moves (utils/talk.js): the style fills it
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
export function resolvePortraitTexture(scene, speaker) {
    if (!speaker) return null;
    const override = scene.dialogPortraits && scene.dialogPortraits[speaker];
    if (override && scene.textures.exists(override.key ?? override)) return override;

    // Normalize: strip accents (Strážce → strazce), lowercase, drop non-alphanumerics.
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
