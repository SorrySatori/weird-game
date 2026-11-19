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
