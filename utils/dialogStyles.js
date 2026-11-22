/**
 * dialogStyles.js: the two presentations of the dialogue the player picks between in Settings (the entry point and the
 * shared helpers are in utils/dialogLayouts.js). Each renderer gets the same normalized model and only builds
 * GameObjects into scene.dialogBox; the options carry their own navigation (commit → opt.activate).
 *
 *   bubbles  in the world: the line in a plate over the speaker, the replies in a plate over the protagonist
 *   cinema   letterbox bars, the line as a subtitle in the bottom bar beside the speaker's portrait, the replies on the right
 *
 * Both keep their size from line to line (fixed plate widths, a fixed bar), so nothing jumps when a reply is clicked.
 * Text is the UI font at 22 px and every plate sits on the UI layer's 2x grid.
 */
import { UI_FONT, UI_SIZE, FRAME, drawPixelFrame, drawPixelTail } from './pixelFrame.js';
import { commit, attachScroll, newBox, resolvePortraitTexture } from './dialogLayouts.js';
import { faceX } from './talk.js';

const INK = '#c8e6d0', DIM = '#5f7a68', NAME = '#e8c46a', GOLD = 0xe8c46a, RIM = FRAME.rim;
const even = v => Math.round(v / 2) * 2;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

function txt(scene, x, y, s, fill, { wrap, align = 'left', lineSpacing = 6, size = UI_SIZE } = {}) {
    return scene.add.text(even(x), even(y), s, {
        fontFamily: UI_FONT, fontSize: size, fill, align, lineSpacing,
        wordWrap: wrap ? { width: wrap } : undefined,
    });
}

/** `h` cut down to whole lines of text `t` (so a scrolling view never shows half a line). */
function fitLines(t, h, lineSpacing = 6) {
    const n = t.getWrappedText().length || 1;
    const step = (t.height + lineSpacing) / n;
    return Math.min(h, Math.floor(Math.max(1, Math.floor((h + lineSpacing) / step)) * step - lineSpacing) + 2);
}

/** A mask shape off the display list (cleaned with the dialog by GameScene.clearDialogLayoutArtifacts). */
function maskRect(scene, x, y, w, h) {
    const g = scene.make.graphics({}, false).setScrollFactor(0);   // on the screen, like the dialog box
    g.fillStyle(0xffffff);
    g.fillRect(x, y, w, h);
    (scene._dialogMasks = scene._dialogMasks || []).push(g);
    return new Phaser.Display.Masks.GeometryMask(scene, g);
}

// ------------------------------------------------------------------ the speaker's figure

const BOUNDS = new Map();   // texture#frame → the opaque box inside the frame

/** The rows / columns a frame actually paints (frames carry empty margins around the figure). */
function opaqueBounds(scene, key, frameName) {
    const f = scene.textures.getFrame(key, frameName);
    if (!f) return null;
    const id = `${key}#${f.name}`;
    if (BOUNDS.has(id)) return BOUNDS.get(id);
    let b = { left: 0, top: 0, right: f.width, bottom: f.height };
    try {
        const w = f.cutWidth, h = f.cutHeight;
        const c = document.createElement('canvas');
        c.width = w; c.height = h;
        const ctx = c.getContext('2d', { willReadFrequently: true });
        ctx.drawImage(f.source.image, f.cutX, f.cutY, w, h, 0, 0, w, h);
        const d = ctx.getImageData(0, 0, w, h).data;
        let l = w, t = h, r = -1, btm = -1;
        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                if (d[(y * w + x) * 4 + 3] > 24) {
                    if (x < l) l = x; if (x > r) r = x;
                    if (y < t) t = y; if (y > btm) btm = y;
                }
            }
        }
        if (r >= 0) b = { left: l, top: t, right: r + 1, bottom: btm + 1 };
    } catch (e) { /* a tainted or odd source: the whole frame */ }
    BOUNDS.set(id, b);
    return b;
}

/**
 * The speaker as a figure: the texture + frame the portrait lookup finds (the scene's own sprite, or the bust override's
 * sheet shown whole) and the sprite standing in the world with it, if any.
 */
function figureOf(scene, model) {
    const p = resolvePortraitTexture(scene, model.speaker) || resolvePortraitTexture(scene, model.speakerEn);
    if (!p) return null;
    const key = p.key ?? p;
    if (!scene.textures.exists(key)) return null;
    const tex = scene.textures.get(key);
    const frame = p.frame != null && tex.has(p.frame) ? p.frame : (tex.has(0) ? 0 : '__BASE');
    const f = tex.get(frame);
    if (!f || f.width > 600) return null;                     // a background, not a character
    const world = scene.children.list.find(o => (o.type === 'Sprite' || o.type === 'Image') && o.visible
        && o.texture?.key === key && o !== scene.priest && o.displayWidth < 600) || null;
    return { key, frame, world, bounds: opaqueBounds(scene, key, frame) };
}

/** The opaque box of a sprite standing in the world (container offsets added, a mirrored sprite mirrored). */
function worldBox(scene, obj) {
    if (!obj?.frame) return null;
    const sx = Math.abs(obj.scaleX), sy = Math.abs(obj.scaleY);
    let ox = 0, oy = 0;
    for (let c = obj.parentContainer; c; c = c.parentContainer) { ox += c.x; oy += c.y; }
    const left0 = ox + obj.x - obj.displayOriginX * sx, top0 = oy + obj.y - obj.displayOriginY * sy;
    const fw = obj.frame.width;
    const b = opaqueBounds(scene, obj.texture.key, obj.frame.name) || { left: 0, top: 0, right: fw, bottom: obj.frame.height };
    const mirrored = obj.flipX !== (obj.scaleX < 0);
    const l = mirrored ? fw - b.right : b.left, r = mirrored ? fw - b.left : b.right;
    return { x: left0 + (l + r) / 2 * sx, left: left0 + l * sx, right: left0 + r * sx, top: top0 + b.top * sy, bottom: top0 + b.bottom * sy };
}

/**
 * The figure drawn big: 2x for a character sheet (the UI layer's grid), small sprites (symbionts, faces) up to ~160 px.
 * Placed by its painted area: `cx` its middle, then `bottom` its lowest painted row or `top` its highest. It moves as
 * it does in the world (the same animation) and faces the same way.
 */
function addFigure(scene, parent, fig, { cx, bottom, top, zoom: z, mirror, anim: animKey }) {
    const b = fig.bounds, bw = b.right - b.left, bh = b.bottom - b.top;
    const zoom = z ?? (bh >= 96 ? 2 : Math.max(2, Math.floor(160 / Math.max(bw, bh))));
    const spr = scene.add.sprite(0, 0, fig.key, fig.frame).setOrigin(0, 0).setScale(zoom);
    const fw = spr.frame.width;
    const mirrored = mirror ?? (!!fig.world && (fig.world.flipX !== (fig.world.scaleX < 0)));
    spr.setFlipX(mirrored);
    const l = mirrored ? fw - b.right : b.left, r = mirrored ? fw - b.left : b.right;
    spr.x = even(cx - (l + r) / 2 * zoom);
    spr.y = even(bottom != null ? bottom - b.bottom * zoom : top - b.top * zoom);
    const anim = animKey !== undefined ? (animKey && { key: animKey, frames: [{ textureKey: fig.key }] })
        : fig.world?.anims?.isPlaying && fig.world.anims.currentAnim;
    if (anim && anim.frames[0]?.textureKey === fig.key) spr.play(anim.key);
    parent.add(spr);
    return { spr, zoom, left: spr.x + l * zoom, right: spr.x + r * zoom, top: spr.y + b.top * zoom, bottom: spr.y + b.bottom * zoom };
}

/**
 * The animation a portrait plays: the world sprite's own while it idles; while it walks (Kloor pacing his stall), the
 * sheet's idle animation, or none (the still frame). A portrait doesn't walk.
 */
function portraitAnim(scene, fig) {
    const moving = a => /walk|run|move/i.test(a.key);
    const cur = fig.world?.anims?.isPlaying && fig.world.anims.currentAnim;
    if (cur && cur.frames[0]?.textureKey === fig.key && !moving(cur)) return cur.key;
    const idle = scene.anims.anims.getArray().find(a => /idle/i.test(a.key) && a.frames[0]?.textureKey === fig.key && !moving(a));
    return idle?.key || null;
}

// ------------------------------------------------------------------ replies

/**
 * One clickable reply at (x, y) of `parent`. s: { wrap, color, hover, used, close, marker, markerColor, markerW,
 * pill (a fill behind the hovered label), pillText, padX, padY }. Returns its height.
 */
function choice(scene, parent, x, y, opt, s) {
    const base = opt.isClose ? (s.close ?? s.used) : (opt.used ? s.used : s.color);
    const mw = s.marker ? (s.markerW ?? 26) : 0;
    const padX = s.padX ?? 6, padY = s.padY ?? 4;
    const label = txt(scene, x + mw, y, opt.label, base, { wrap: s.wrap - mw, lineSpacing: 4 });
    const h = label.height;
    let pill = null, marker = null;
    if (s.pill != null) {
        pill = scene.add.rectangle(even(x + mw - padX), even(y - padY), even(label.width + 2 * padX), even(h + 2 * padY), s.pill, 1)
            .setOrigin(0, 0).setVisible(false);
        parent.add(pill);
    }
    if (s.marker) {
        marker = txt(scene, x, y, s.marker, s.markerColor ?? s.hover).setVisible(false);
        parent.add(marker);
    }
    const hit = scene.add.rectangle(x - padX, y - padY, s.wrap + 2 * padX, h + 2 * padY, 0xffffff, 0.001).setOrigin(0, 0);
    hit.setInteractive({ useHandCursor: true });
    parent.add([label, hit]);
    hit.on('pointerover', () => { label.setFill(pill ? s.pillText : s.hover); pill?.setVisible(true); marker?.setVisible(true); });
    hit.on('pointerout', () => { label.setFill(base); pill?.setVisible(false); marker?.setVisible(false); });
    hit.on('pointerdown', () => { hit.disableInteractive(); commit(scene, opt); });
    return h;
}

/**
 * Replies stacked from (x, 0) in a new container; returns { c, h, fit } where fit(max) is the tallest view up to `max`
 * that ends with a whole reply (a scrolling list never opens on half a reply).
 */
function choiceList(scene, parent, x, model, s, gap = 10) {
    const c = scene.add.container(x, 0);
    parent.add(c);
    let y = 0;
    const ends = [];
    model.options.forEach((opt, i) => {
        y += even(choice(scene, c, 0, y, opt, s));
        ends.push(y);
        if (i < model.options.length - 1) y += gap;
    });
    const fit = max => (y <= max ? y : Math.max(ends[0] ?? 0, ...ends.filter(e => e <= max)));
    return { c, h: y, fit };
}

// ------------------------------------------------------------------ the styles

export const STYLE_RENDERERS = {
    // ---- BUBBLES: no panel, the conversation happens over the heads in the scene: the line in a plate over the
    // speaker, the replies in a plate over the protagonist; where the two would meet, they stand side by side.
    // Both plates keep one width (only their height follows the text), so a click doesn't make them jump
    bubbles(scene, model) {
        const box = newBox(scene);
        const W = scene.scale.width, H = scene.scale.height, M = 14, PAD = 14, G = 2, GAP = 16, TAB = 18;
        const fig = figureOf(scene, model);
        scene._dialogSpeakers = [fig?.world];
        const a = worldBox(scene, fig?.world);                     // none: a narrator, a face in the wall
        const ax = a ? a.x : W / 2;
        const p = worldBox(scene, scene.priest) || { x: W / 2, top: H - 80 };

        /** A plate at (x, y) w x h, its stepped tail pointing down at `tailX` (null: none). */
        const plate = (x, y, w, h, rim, tailX) => {
            const g = scene.add.graphics();
            box.add(g);
            drawPixelFrame(g, x, y, w, h, { rim, alpha: 0.95, round: true });
            if (tailX != null) drawPixelTail(g, tailX, y + h - G + 6 * G, 6, 'down', { rim, fill: FRAME.fill });
            return g;
        };

        // sizes: fixed widths with a gutter on the right for the scroll arrows; the line's plate as tall as the room over
        // the speaker's head allows (a longer line scrolls)
        const LW = 360, mw = 26, ARROWS = 16;
        const cw = even(LW + mw + 2 * PAD + ARROWS);
        const opts = choiceList(scene, box, 0, model, {
            wrap: LW + mw, color: INK, hover: NAME, used: DIM, close: '#8a9a8e', pill: GOLD, pillText: '#10160f',
            marker: '▶', markerColor: NAME, markerW: mw,
        }, 8);
        const optH = opts.fit(Math.max(120, p.top - 20 - M - 2 * PAD));
        const ch = even(optH + 2 * PAD);

        const TW = 420;
        const body = model.text ? txt(scene, 0, 0, model.text, INK, { wrap: TW, lineSpacing: 4 }) : null;
        const name = body && model.speaker ? txt(scene, 0, 0, model.speaker, NAME) : null;
        const nameW = name ? even(name.width + 20) : 0;
        const room = (a ? a.top - 20 : H * 0.55) - (M + TAB) - 2 * PAD - (name ? 8 : 0);
        const bodyH = body ? fitLines(body, Math.min(body.height, Math.max(120, room)), 4) : 0;
        const bw = body ? even(TW + 2 * PAD + ARROWS) : 0, bh = body ? even(bodyH + 2 * PAD + (name ? 8 : 0)) : 0;

        // where: each over its own head (pushed inside the screen first: a plate over someone at the edge reaches further
        // in), side by side where they'd meet (the replies on the protagonist's side), one over the other if that's too
        // wide. Whether they meet is judged by the widths alone (they're fixed), so the arrangement holds for the whole
        // conversation instead of flipping with a line's height
        let lx = clamp(ax - bw / 2, M, W - M - bw), ly = Math.max(M + TAB, a ? a.top - 20 - bh : 70);
        let cx = clamp(p.x - cw / 2, M, W - M - cw), cy = Math.max(M, p.top - 20 - ch);
        const meet = body && lx < cx + cw + GAP && cx < lx + bw + GAP;
        if (meet) {
            const total = bw + GAP + cw;
            if (total <= W - 2 * M) {
                const left = clamp((p.x + ax) / 2 - total / 2, M, W - M - total);
                if (p.x <= ax) { cx = left; lx = left + cw + GAP; } else { lx = left; cx = left + bw + GAP; }
            } else {
                ly = M + TAB;
                cy = Math.max(cy, ly + bh + GAP);
            }
        }
        lx = even(lx); ly = even(ly);
        cx = even(cx); cy = even(cy);
        const tailAt = (x, w, y, h, at, top) => (at > x + 16 && at < x + w - 16 && y + h + 12 < top ? at : null);

        if (body) {
            plate(lx, ly, bw, bh, RIM, a ? tailAt(lx, bw, ly, bh, a.x, a.top) : null);
            if (name) {                                             // a name tab over the plate's top-left corner
                const tab = scene.add.graphics();
                drawPixelFrame(tab, lx + 12, ly - 16, nameW, 30, { rim: RIM, alpha: 1 });
                name.setPosition(even(lx + 22), even(ly - 12));
                box.add([tab, name]);
            }
            body.setPosition(even(lx + PAD), even(ly + PAD + (name ? 8 : 0)));
            box.add(body);
            attachScroll(scene, body, body.height, { x: lx + PAD - 4, y: body.y, w: bw - PAD - 2, h: bodyH, arrowColor: NAME });
        }
        box.moveTo(plate(cx, cy, cw, ch, 0x5f8a6e, tailAt(cx, cw, cy, ch, p.x, p.top)), box.getIndex(opts.c));
        // the notices keep clear of both plates (with the name tab and the tails)
        scene._noticeAvoid = [{ x: cx, y: cy, w: cw, h: ch + 14 }];
        if (body) scene._noticeAvoid.push({ x: lx, y: ly - 18, w: bw, h: bh + 32 });
        opts.c.setPosition(cx + PAD, cy + PAD);
        attachScroll(scene, opts.c, opts.h, { x: cx + 4, y: cy + PAD, w: cw - 8, h: optH, arrowColor: NAME });
    },

    // ---- CINEMA: letterbox bars; the line is a subtitle beside the speaker's portrait, the replies float on the right
    cinema(scene, model) {
        const box = newBox(scene);
        const W = scene.scale.width, H = scene.scale.height;
        const TOPBAR = 48, TX = 200, TW = 820, LINES = 5, LS = 4;

        // the bottom bar has one height for every line (it jumped with the text's length): room for the name and
        // LINES lines, a longer line scrolls
        const name = model.speaker ? txt(scene, TX, 0, model.speaker.toUpperCase(), '#8b928d') : null;
        const body = txt(scene, TX, 0, model.text, '#ecebe2', { wrap: TW, lineSpacing: LS });
        const probe = txt(scene, 0, 0, Array(LINES).fill('M').join('\n'), '#000', { lineSpacing: LS });
        const linesH = probe.height;
        probe.destroy();
        const nameH = 34;
        const barH = even(22 + nameH + linesH + 20);
        const barTop = H - barH;

        const g = scene.add.graphics();
        box.add(g);
        g.fillStyle(0x000000, 0.2);
        g.fillRect(0, TOPBAR, W, barTop - TOPBAR);
        const shadeX = even(W * 0.45);
        g.fillGradientStyle(0, 0, 0, 0, 0, 0.8, 0, 0.8);            // the right side darkens under the replies
        g.fillRect(shadeX, TOPBAR, W - shadeX, barTop - TOPBAR);

        const topBar = scene.add.rectangle(0, 0, W, TOPBAR, 0x000000, 1).setOrigin(0, 0);
        const bottom = scene.add.container(0, 0);
        bottom.add(scene.add.rectangle(0, barTop, W, barH, 0x000000, 0.96).setOrigin(0, 0));
        box.add([topBar, bottom]);
        const textTop = barTop + 22 + (name ? nameH : 0);
        if (name) { name.y = barTop + 22; bottom.add(name); }
        body.y = textTop;
        bottom.add(body);
        attachScroll(scene, body, body.height, { x: TX - 8, y: textTop, w: TW + 40, h: fitLines(body, H - 20 - textTop, LS), arrowColor: NAME });

        // the speaker's portrait left of the subtitle: their bust (a scene's tuned { zoom, top } bust if it has one, else
        // the figure's top at 2x), a small sprite whole; it moves as they do in the world. The text keeps its place
        // without one (a narrator), so it doesn't jump between lines.
        let portraitMask = null;
        const fig = figureOf(scene, model);
        if (fig) {
            const PX = 24, PY = barTop + 22, PW = TX - 48, PH = barH - 44, pcx = PX + PW / 2;
            const frame = scene.add.graphics();
            drawPixelFrame(frame, PX, PY, PW, PH, { fill: 0x0e1210, alpha: 1, rim: 0x4a4f4b });
            bottom.add(frame);
            const ov = scene.dialogPortraits?.[model.speaker] || scene.dialogPortraits?.[model.speakerEn];
            const b = fig.bounds, bw = b.right - b.left, bh = b.bottom - b.top;
            // the portrait holds still in its frame: the sheet as drawn (not mirrored as the sprite walks back and
            // forth), idling, and a figure wider than the frame centred on its face (Kloor's snout, not his middle),
            // never so far that the frame shows empty space past the figure's edge
            const look = { mirror: false, anim: portraitAnim(scene, fig) };
            const across = z => {
                const w = bw * z, mid = (b.left + b.right) / 2;
                if (w <= PW - 8) return pcx;
                return clamp(pcx - ((faceX(fig.key) ?? mid) - mid) * z, PX + PW - 6 - w / 2, PX + 6 + w / 2);
            };
            let f;
            if (ov?.zoom) {
                f = addFigure(scene, bottom, fig, { ...look, cx: across(ov.zoom), top: PY + 4 + (b.top - (ov.top || 0)) * ov.zoom, zoom: ov.zoom });
            } else if (bh >= 96) {
                f = addFigure(scene, bottom, fig, { ...look, cx: across(2), top: PY + 10, zoom: 2 });
            } else {
                const z = Math.max(1, Math.floor(Math.min(PW - 16, PH - 16) / Math.max(bw, bh)));
                f = addFigure(scene, bottom, fig, { ...look, cx: pcx, top: PY + (PH - bh * z) / 2, zoom: z });
            }
            portraitMask = maskRect(scene, PX + 2, PY + 2, PW - 4, PH - 4);
            f.spr.setMask(portraitMask);
            scene._dialogSpeakers = [fig.world, f.spr];
        }

        const RX = 680, RW = W - 36 - RX, MW = 44;
        // the notices go into the top bar in a row from the right (past the HUD medallion they wrap left of the replies)
        scene._noticeSpot = { row: true, right: W - 20, left: 120, y: TOPBAR / 2, wrapRight: RX - MW - 20 };
        const opts = choiceList(scene, box, RX - MW, model, {
            wrap: RW + MW, color: '#d8d7ce', hover: '#ffffff', used: '#6f746f', close: '#8b928d', marker: '•••', markerColor: NAME, markerW: MW,
        }, 8);
        const room = barTop - TOPBAR - 28;
        const oh = opts.fit(room);
        opts.c.y = even(TOPBAR + 14 + (room - oh) / 2);
        attachScroll(scene, opts.c, opts.h, { x: RX - MW - 8, y: opts.c.y, w: RW + MW + 16, h: oh, arrowColor: NAME });

        if (model.fresh) {                                          // the bars close in when a conversation starts
            scene.tweens.add({ targets: topBar, y: { from: -TOPBAR, to: 0 }, duration: 280, ease: 'Cubic.easeOut' });
            scene.tweens.add({ targets: [bottom, portraitMask?.geometryMask].filter(Boolean), y: { from: barH, to: 0 }, duration: 280, ease: 'Cubic.easeOut' });
            scene.tweens.add({ targets: [g, opts.c], alpha: { from: 0, to: 1 }, duration: 320, delay: 120 });
        }
    },
};
