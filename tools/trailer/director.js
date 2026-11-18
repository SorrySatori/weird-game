// Trailer director: runs inside capture.html, drives the game frame by frame on the virtual clock and
// records the shots from shots.js. --survey instead saves a still + object dump of every demo scene,
// --dialogs a still of sample conversations in every dialog style (out/stills/dialog_<case>_<style>.png).
import { SHOTS, STILLS, SURVEY_SCENES, HUD, DIALOG_CASES } from './shots.js';
import { DIALOG_STYLES, cycleDialogStyle } from '../../utils/dialogLayouts.js';
import { setSetting } from '../../systems/GameSettings.js';

const cap = window.__cap;
const vt = window.__vt;
const W = 1067, H = 600;
const FPS = cap.args.fps;
const DT = 1000 / FPS;

let game;
const pixels = new Uint8Array(W * H * 4);

function readPixels() {
    const gl = game.renderer.gl;
    gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    return pixels;
}

// One frame of game time; recorded frames go to the encoder, the rest just let real I/O breathe.
async function frame(record) {
    vt.tick(DT);
    if (record) await cap.frame(readPixels());
    else await vt.yieldReal();
}

async function until(cond, maxFrames = 60 * FPS, what = 'condition') {
    for (let i = 0; i < maxFrames; i++) {
        if (cond()) return;
        await frame(false);
    }
    throw new Error(`timed out waiting for ${what}`);
}

const wait = async (seconds) => { for (let i = 0, n = Math.round(seconds * FPS); i < n; i++) await frame(false); };

// Stop whatever runs and start `key` fresh; resolves once its create() has finished.
async function enter(key, data = {}) {
    const sm = game.scene;
    for (const s of sm.getScenes(true)) s.scene.stop();
    await frame(false);
    const scene = sm.getScene(key);
    let created = false;
    scene.events.once('create', () => { created = true; });
    sm.start(key, data);
    await until(() => created, 120 * FPS, `${key} create`);
    return scene;
}

function describe(scene) {
    // containers are walked too (the HUD lives in them); `scale` is the on-screen one (container scales multiplied in),
    // `src` the texture's file, so the art's pixel grid can be audited per file
    const out = [];
    const walk = (list, parentScale = 1, parent) => list.forEach(o => {
        const scale = +((o.scaleX ?? 1) * parentScale).toFixed(3);
        const src = o.texture?.source?.[0]?.image?.src;
        out.push({
            type: o.type,
            tex: o.texture?.key,
            frame: o.frame?.name,
            name: o.name || undefined,
            parent,
            src: src && !src.startsWith('data:') ? decodeURI(src.replace(/^.*?\/assets\//, 'assets/')) : undefined,
            text: o.text ? String(o.text).slice(0, 60) : undefined,
            x: Math.round(o.x), y: Math.round(o.y),
            w: Math.round(o.displayWidth || o.width || 0), h: Math.round(o.displayHeight || o.height || 0),
            scale, depth: o.depth, sf: o.scrollFactorX, vis: o.visible, alpha: +(o.alpha ?? 1).toFixed(2),
            input: !!o.input,
        });
        if (o.list) walk(o.list, scale, o.name || o.type);
    });
    walk(scene.children.list);
    return out;
}

async function survey() {
    for (const key of cap.args.only || SURVEY_SCENES) {
        try {
            const scene = await enter(key);
            await wait(2.5);
            const cam = scene.cameras.main;
            await cap.json(key, {
                camera: { scrollX: cam.scrollX, scrollY: cam.scrollY, zoom: cam.zoom, bounds: cam.useBounds ? { ...cam._bounds } : null },
                objects: describe(scene),
            });
            await cap.still(key, readPixels());
            cap.log(`survey ${key}: ${scene.children.list.length} objects`);
        } catch (e) {
            cap.log(`survey ${key} FAILED: ${e.stack || e}`);
        }
    }
}

async function dialogs() {
    await enter('EntryScene'); // the registry systems
    for (const c of cap.args.only ? DIALOG_CASES.filter(d => cap.args.only.includes(d.id)) : DIALOG_CASES) {
        try {
            setSetting('dialogStyle', DIALOG_STYLES[0]);
            if (c.menu) {   // the Settings panel with its dialog-style row
                await enter(c.scene, c.data);
                await wait(1);
                await cap.still(`dialog_${c.id}`, readPixels());
                continue;
            }
            const scene = await enter(c.scene);
            scene.isTransitioning = true;
            scene.time.removeAllEvents();   // arrival dialogs and timers
            await wait(0.5);
            scene.hideDialog();
            if (scene.priest && c.x != null) scene.priest.x = c.x;
            scene.showDialog(c.state);
            for (const pick of c.picks || []) {   // walk the conversation as a click would (the reply goes in the transcript)
                await wait(0.2);
                const opt = scene._dialogModel.options[pick];
                scene._dialogLog?.push({ reply: opt.label });
                opt.activate();
            }
            for (const style of DIALOG_STYLES) {
                if (style !== DIALOG_STYLES[0]) cycleDialogStyle(scene, 1);
                await wait(0.3);
                const hits = [], walk = o => { if (o.type === 'Rectangle' && o.input?.enabled) hits.push(o); o.list?.forEach(walk); };
                walk(scene.dialogBox);
                hits[c.hover ?? 0]?.emit('pointerover');   // a reply under the pointer, to show the hover state
                await wait(0.1);
                await cap.still(`dialog_${c.id}_${style}`, readPixels());
            }
            cap.log(`dialogs ${c.id}`);
        } catch (e) {
            cap.log(`dialogs ${c.id} FAILED: ${e.stack || e}`);
        }
    }
}

async function shoot() {
    const list = cap.args.only ? SHOTS.filter(s => cap.args.only.includes(s.id)) : SHOTS;
    await enter('EntryScene'); // creates the registry systems (G/D, symbionts…) that `before` hooks touch
    for (const shot of list) {
        shot.before?.(game);
        const scene = await enter(shot.scene, shot.data);
        const ctx = { scene, game, fps: FPS, t: 0, frame: 0, keep: new Set() };
        scene.isTransitioning = true; // no edge exits or exit zones while the shot plays
        const hud = () => HUD[shot.hud](ctx);
        if (shot.hud) scene.sys.events.on('prerender', hud); // scene emitters outlive restarts: removed below
        await shot.setup?.(ctx, { wait, frame, until });
        scene.cameras.main.resetFX();
        await frame(false);
        await cap.begin(shot.id);
        const n = Math.round(shot.duration * FPS);
        for (let i = 0; i < n; i++) {
            ctx.frame = i;
            ctx.t = i / FPS;
            shot.update?.(ctx);
            await frame(true);
        }
        await cap.end();
        scene.sys.events.off('prerender', hud);
        shot.after?.(ctx);
    }
}

async function screenshots() {
    const list = cap.args.only ? STILLS.filter(s => cap.args.only.includes(s.id)) : STILLS;
    await enter('EntryScene');
    for (const shot of list) {
        shot.before?.(game);
        const scene = await enter(shot.scene, shot.data);
        const ctx = { scene, game, fps: FPS, t: 0, frame: 0, keep: new Set() };
        scene.isTransitioning = true;
        const hud = () => HUD[shot.hud](ctx);
        if (shot.hud) scene.sys.events.on('prerender', hud);
        await shot.setup?.(ctx, { wait, frame, until });
        scene.cameras.main.resetFX();
        await wait(shot.at);
        await cap.still(shot.id, readPixels(), !shot.native);   // native: true -> out/stills at 1067x600 (pixel checks)
        scene.sys.events.off('prerender', hud);
        cap.log(`screenshot ${shot.id}`);
    }
}

(async () => {
    try {
        await until(() => window.__game?.isBooted && window.__game.renderer?.gl, 60 * FPS, 'game boot');
        game = window.__game;
        // Let LoadingScene pull the shared assets (item icons, recordings) before any scene is entered.
        await until(() => {
            const loading = game.scene.getScene('LoadingScene');
            return loading && loading.sys.settings.status >= Phaser.Scenes.CREATING;
        }, 120 * FPS, 'LoadingScene');
        if (cap.args.survey) await survey();
        else if (cap.args.screenshots) await screenshots();
        else if (cap.args.dialogs) await dialogs();
        else await shoot();
        await cap.finish(0);
    } catch (e) {
        cap.log(`director FAILED: ${e.stack || e}`);
        await cap.finish(1);
    }
})();
