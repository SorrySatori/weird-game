// Scripted playthrough of the Steam demo (config/build.js DEMO_BUILD): new game -> the end card, with the side quests,
// asserting the game state at every beat. Runs in the trailer harness (tools/trailer/director.js --test):
//
//   ./tools/trailer/capture.sh --test playthrough [--lang cs] [--only skyship|alt|button|tutorial|dispensation|temporary|firstkey|firstzerren]
//
// Branches (--only):
//   main     (default) Thorne-Still from the corpse, Kloor's Vestigel (Zerren -> Edgar's book), Gnur's living core,
//            Ortolan's arms (Artisan's form), the Lift-Mother on both stories, Dr. Elphi, the bus, the end card.
//   skyship  the either/or: spores into the corpse, the skyship and Captain Liris's tool, Ulvarex on a Violet Oltrac
//            trip, Gnur refused -> the Applications clerk's Bishop trail, the Lift-Mother on the tool, the bus.
//   button   Gnur's core wrenched out (he pays 30) -> Zerren's Forgotten Elevator Button (75) -> the Lift-Mother on the button
//            alone (one story, no tool), Dr. Elphi's "stop guessing" opener, the bus, the end card.
//   tutorial Thaal's equipment tutorial played through (the HUD panels opened by real clicks), then Ortolan's arms on the
//            Inherited Deformity Form (-> the legged shark).
//   dispensation / temporary   Ortolan's arms on the Special Dispensation (-> Black Cactus) / the Temporary Permit
//            (-> Maxim Hopsalot): the Applications clerk's clue, the dream queue's choices, the Senior Clerk, the gift.
//   firstkey / firstzerren   the first panel of a fresh session opened by the J key / by Zerren's stall (both run
//            inside a Phaser step: see firstPanelByKey).
//   alt      the other ways: Thorne-Still declined, Ulvarex on the Scraper roof, Zerren persuaded, Gnur fooled with
//            Ulvarex's mirage core (-> the clerk), Edgar's book first (Ulvarex's villain), Ravla's forgery redone by
//            Ulvarex's inspector -> Ortolan's forged-permit gift, spores sold to Kloor, Dr. Elphi's other openers, the bus.
//
// The player's actions are real where it is cheap: NPCs and exits get a DOM click on the canvas at a point where they
// are the topmost hit (Phaser's own hit test), so an exit or a person hidden under something else shows up as a WARN
// (then the pointerdown is emitted directly so the run goes on). Dialog options are picked by their key through the
// dialog model's activate() -- exactly what a click on the option runs. Shops are bought from through ShopSystem.buyItem.
// Every line printed: PASS / FAIL / WARN / RESCUE (a failed step worked around so the rest can still be tested) /
// I18N (Czech run: English or raw keys on screen). Stills: out/stills/pt_<lang>_<branch>_NN_<beat>.png;
// the dialog transcript: out/stills/pt_<lang>_<branch>_transcript.json.
import SceneTransitionManager from '../../../utils/SceneTransitionManager.js';
import LanguageSystem from '../../../systems/LanguageSystem.js';
import GameScene from '../../../scenes/GameScene.js';
import { armsReward } from '../../../utils/OrtolanArms.js';
import { hudButtonPos } from '../../../utils/hudButton.js';

export default async function playthrough({ game, cap, enter, wait, frame, until, readPixels }) {
    const LANG = cap.args.lang || 'en';
    const CS = LANG === 'cs';
    const BRANCH = (cap.args.only && cap.args.only[0]) || 'main';
    const W = game.scale.width, H = game.scale.height;
    const L = LanguageSystem.getInstance();
    const tag = `${LANG}_${BRANCH}`;

    // ------------------------------------------------------------------ reporting
    const results = [];
    let beat = 'boot';
    const log = (...a) => cap.log(...a);
    const pass = (msg) => { results.push({ ok: true, beat, msg }); log(`PASS [${beat}] ${msg}`); };
    const fail = (msg) => { results.push({ ok: false, beat, msg }); log(`FAIL [${beat}] ${msg}`); };
    const warns = [];
    const warn = (msg) => { warns.push({ beat, msg }); log(`WARN [${beat}] ${msg}`); };
    const rescues = [];
    const rescue = (msg) => { rescues.push({ beat, msg }); log(`RESCUE [${beat}] ${msg}`); };
    const check = (cond, msg, detail = '') => { if (cond) pass(msg); else fail(msg + (detail ? ` -- ${detail}` : '')); return !!cond; };

    // console errors / warnings and uncaught errors, per beat
    const consoleLog = [];
    for (const lvl of ['error', 'warn']) {
        const orig = console[lvl];
        console[lvl] = function (...a) {
            const msg = a.map(x => (x && x.stack) || (typeof x === 'string' ? x : safe(x))).join(' ');
            consoleLog.push({ lvl, beat, msg: msg.slice(0, 600) });
            return orig.apply(this, a);
        };
    }
    window.addEventListener('error', e => consoleLog.push({ lvl: 'uncaught', beat, msg: String(e.error?.stack || e.message).slice(0, 600) }));
    window.addEventListener('unhandledrejection', e => consoleLog.push({ lvl: 'rejection', beat, msg: String(e.reason?.stack || e.reason).slice(0, 600) }));
    function safe(x) { try { return JSON.stringify(x); } catch (e) { return String(x); } }

    // ------------------------------------------------------------------ i18n audit
    const issues = new Map();   // kind|where|text -> { kind, where, text, beat }
    const issue = (kind, where, text) => {
        const k = `${kind}|${where}|${text}`;
        if (issues.has(k)) return;
        issues.set(k, { kind, where, text, beat });
        log(`I18N [${beat}] ${kind} @ ${where}: ${String(text).replace(/\n/g, ' / ').slice(0, 160)}`);
    };
    const EN_WORDS = /\b(the|and|you|your|what|with|this|that|is|are|have|for|I'm|don't|can't|of|was|it's|here|there|about|who|will|would)\b/i;
    const EN_SINGLE = new Set(['Continue', 'Leave', 'Back', 'Thanks', 'Thank you', 'Deal', 'Close', 'Step out', 'Upstairs', 'Downstairs',
        'Inside', 'Outside', 'Use', 'Buy', 'Sell', 'Exit', 'Crossroads', 'Not yet', 'OK.', 'Leave.']);
    const looksEnglish = (s) => {
        const t = String(s).replace(/\*[^*]*\*/g, ' ').trim();
        if (!t) return false;
        if (EN_SINGLE.has(t)) return true;
        return EN_WORDS.test(t) && !/[áčďéěíňóřšťúůýž]/i.test(t);
    };
    const RAWKEY = /(^|\s)(ui|notifications|observe|locations|exits|items|shop|journal|quests|intro|entry|crossroad|skyship|scraperAmbra|shedRegistration|ambient|symbionts)\.[a-zA-Z_][\w.]*\b/;
    function auditText(text, where) {
        if (text == null) return;
        const s = String(text).trim();
        if (!s) return;
        if (RAWKEY.test(s)) issue('raw-key', where, s);
        if (/\bundefined\b|\bNaN\b|\[object Object\]|\{[A-Za-z_^][\w.:|]*\}/.test(s)) issue('placeholder', where, s);
        if (/\\n/.test(s)) issue('literal-backslash-n', where, s);
        if (CS && looksEnglish(s)) issue('english-in-cs', where, s);
    }

    // LanguageSystem.t(): keys missing in the current language (EN fallback in Czech, or missing everywhere)
    const tMisses = new Map();
    {
        const protoT = Object.getPrototypeOf(L).t;
        L.t = function (key, params) {
            const v = protoT.call(this, key, params);
            if (typeof key === 'string' && this.currentLanguage === LANG) {
                const own = this._resolve(this.languages[this.currentLanguage] || {}, key);
                if (own === undefined) {
                    const kind = v === key ? 'missing-everywhere' : 'en-fallback';
                    const k = `${kind}|${key}`;
                    if (!tMisses.has(k)) tMisses.set(k, { kind, key, beat, scene: game.registry.get('currentScene') });
                }
            }
            return v;
        };
    }

    // every notification, speech bubble and dialog line goes through the audit (and the transcript)
    const transcript = [];
    const notices = [];   // every corner notice: which scene showed it, and which scene the player was in
    // a notice's text without its {n} (the localized prefix), e.g. the quest-spores reward or an Oltrac dose's swing
    const prefixOf = (key) => { const v = Object.getPrototypeOf(L).t.call(L, key, { n: '\u0000' }); return String(v).split('\u0000')[0]; };
    const isNotice = (text, key) => { const p = prefixOf(key); return !!p && String(text).startsWith(p); };
    const questNoticeKeys = ['notifications.newQuest', 'notifications.questUpdated', 'notifications.questCompleted', 'notifications.questSpores'];
    const noticesSince = (i, key) => notices.slice(i).filter(n => isNotice(n.text, key));
    {
        const P = GameScene.prototype;
        const origNotify = P.showNotification;
        P.showNotification = function (title, ...rest) {
            if (typeof title === 'string') {
                // a symbiont's ambient line ("thorne-still: ...") is translated when it is shown (GameScene.showSymbiontMessage)
                let said = null;
                try { said = this.symbiontLine?.(title); } catch (e) { /* */ }
                auditText(said ? L.symbiontLine(said.text) : title, `${this.scene.key}:${said ? 'symbiont-line' : 'notification'}`);
                transcript.push({ beat, scene: this.scene.key, notification: title });
                notices.push({ beat, scene: this.scene.key, current: game.registry.get('currentScene'), running: this.sys.isActive(), text: title });
            }
            return origNotify.call(this, title, ...rest);
        };
        const origBubble = P.showSpeechBubble;
        P.showSpeechBubble = function (target, message, opts) {
            if (typeof message === 'string') { auditText(message, `${this.scene.key}:bubble`); transcript.push({ beat, scene: this.scene.key, bubble: message }); }
            return origBubble.call(this, target, message, opts);
        };
        const origShow = P.showDialog;
        P.showDialog = function (state) {
            const r = origShow.call(this, state);
            try { auditDialog(this, state); } catch (e) { warn(`dialog audit threw: ${e.message}`); }
            return r;
        };
    }

    function rawState(s, state) {
        if (typeof state !== 'string') return state && typeof state === 'object' ? state : null;
        try { return s.dialogContent?.[state] || null; } catch (e) { return null; }
    }
    function rawOptions(s, state) {
        const st = rawState(s, state);
        let o = st?.options;
        try { if (typeof o === 'function') o = o.call(s); } catch (e) { o = []; }
        return Array.isArray(o) ? o : [];
    }

    function auditDialog(s, state) {
        const m = s._dialogModel;
        if (!s.dialogVisible || !m) return;
        const where = `${s.scene.key}.${typeof state === 'string' ? state : '(object)'}`;
        transcript.push({ beat, scene: s.scene.key, state: typeof state === 'string' ? state : '(object)', speaker: m.speaker,
            text: typeof m.text === 'string' ? m.text : '(fn)', options: m.options.map(o => o.label) });
        const text = typeof m.text === 'function' ? m.text() : m.text;
        if (!text || !String(text).trim()) issue('empty-dialog-text', where, `(options: ${m.options.map(o => o.label).join(' | ')})`);
        auditText(text, `${where}:text`);
        if (m.speaker) auditText(m.speaker, `${where}:speaker`);
        m.options.forEach(o => auditText(o.label, `${where}:option`));
        if (!CS || typeof state !== 'string') return;
        // the Czech text must not be the English text of the same state (translateDialog found nothing)
        const st = rawState(s, state);
        if (st && typeof st.text === 'string' && st.text === text && looksEnglish(text)) issue('untranslated-dialog-text', where, text);
        const raw = rawOptions(s, state);
        raw.forEach((o, i) => { if (m.options[i] && m.options[i].label === o.text && looksEnglish(o.text)) issue('untranslated-option', `${where}:${o.key}`, o.text); });
    }

    // ------------------------------------------------------------------ the scene, the state
    const cur = () => game.scene.getScenes(true).find(sc => sc instanceof GameScene) || null;
    const qs = () => game.registry.get('questSystem');
    const quest = (id) => qs()?.getQuest(id);
    const hasUpd = (id, key) => !!quest(id)?.updates?.some(u => u.key === key);
    const journal = () => cur()?.journalSystem;
    const hasJ = (id) => !!journal()?.getEntry(id);
    const inv = () => game.registry.get('inventory')?.items || [];
    const hasItem = (id) => inv().some(i => i.id === id);
    const money = () => cur()?.moneySystem?.amount ?? null;
    const spores = () => game.registry.get('sporeSystem')?.getSporeLevel?.() ?? null;
    const flags = () => game.registry.get('onceFlags') || [];
    const symbionts = () => game.registry.get('symbiontSystem');
    const qDone = (id) => !!quest(id)?.isComplete;

    let stillN = 0;
    async function still(name) {
        await frame(false);
        const n = String(++stillN).padStart(2, '0');
        await cap.still(`pt_${tag}_${n}_${name}`, readPixels(), false);
    }

    // ------------------------------------------------------------------ input: real clicks on the canvas
    function dom(type, x, y, buttons) {
        const c = game.canvas, r = c.getBoundingClientRect();
        const cx = r.left + x * r.width / W, cy = r.top + y * r.height / H;
        c.dispatchEvent(new MouseEvent(type, { clientX: cx, clientY: cy, button: 0, buttons, bubbles: true, cancelable: true, view: window }));
    }
    async function domClick(x, y) {
        dom('mousemove', x, y, 0);
        dom('mousedown', x, y, 1);
        await frame(false);
        dom('mouseup', x, y, 0);
        await frame(false);
    }
    const label = (o) => o ? `${o.type}${o.texture?.key && o.texture.key !== '__MISSING' ? ':' + o.texture.key : ''}${o.name ? '#' + o.name : ''}${o.__target ? '>' + o.__target : ''}@${Math.round(o.x)},${Math.round(o.y)} d${o.depth}` : 'nothing';
    function hitsAt(s, x, y) {
        const cam = s.cameras.main;
        const list = (s.input._list || []).filter(o => o.input?.enabled);
        const hits = game.input.hitTest({ x, y }, list, cam, []).slice();
        return s.input.sortGameObjects(hits, { camera: cam });
    }
    /** A screen point where `obj` takes the click (topmost there), else one where it is at least hit; null if none. */
    function hitPoint(s, obj) {
        const cam = s.cameras.main;
        if (Math.abs(cam.zoom - 1) > 0.01) return null;
        let b = null;
        try { b = obj.getBounds(); } catch (e) { /* */ }
        // a container's bounds come from its children (Dr. Elphi's is an empty hit box): use its hit area then
        const ha = obj.input?.hitArea;
        if ((!b || b.width < 2 || b.height < 2) && ha?.width) {
            b = { x: obj.x - (obj.displayOriginX || 0) + (ha.x || 0), y: obj.y - (obj.displayOriginY || 0) + (ha.y || 0), width: ha.width, height: ha.height };
        }
        if (!b) return null;
        const sf = obj.scrollFactorX ?? 1;
        const cands = [];
        for (let iy = 0; iy < 11; iy++) for (let ix = 0; ix < 11; ix++) {
            const fx = (ix + 0.5) / 11, fy = (iy + 0.5) / 11;
            cands.push({ wx: b.x + b.width * fx, wy: b.y + b.height * fy, d: (fx - 0.5) ** 2 + (fy - 0.55) ** 2 });
        }
        cands.sort((a, z) => a.d - z.d);
        let fallback = null;
        for (const c of cands) {
            const x = c.wx - cam.scrollX * sf, y = c.wy - cam.scrollY * sf;
            if (x < 2 || y < 2 || x > W - 2 || y > H - 2) continue;
            const hits = hitsAt(s, x, y);
            if (!hits.includes(obj)) continue;
            if (hits[0] === obj) return { x, y, top: true };
            fallback ??= { x, y, top: false, over: hits[0] };
        }
        return fallback;
    }
    /** Click `obj` like a player; falls back to emitting its pointerdown. Returns 'dom' | 'emit'. */
    async function clickObj(obj, what) {
        const s = cur();
        if (!obj || !obj.input) { fail(`${what}: not clickable (${obj ? label(obj) : 'missing'})`); return 'none'; }
        let fired = false;
        const mark = () => { fired = true; };
        obj.once('pointerdown', mark);
        const pt = hitPoint(s, obj);
        if (pt?.top) await domClick(pt.x, pt.y);
        if (!fired) {
            obj.off('pointerdown', mark);
            const why = !pt ? 'no point of it is hit on screen' : !pt.top ? `covered by ${label(pt.over)} at ${Math.round(pt.x)},${Math.round(pt.y)}` : 'the click did not reach it';
            warn(`${what}: a real click can't reach it (${why}); emitting pointerdown`);
            const p = game.input.activePointer;
            obj.emit('pointerdown', p, 0, 0, { stopPropagation() {} });
            await frame(false);
            return 'emit';
        }
        return 'dom';
    }

    // ------------------------------------------------------------------ exits: which zone leads where
    {
        const P = SceneTransitionManager.prototype;
        const wrap = (name, targetOf) => {
            const orig = P[name];
            P[name] = function (...a) {
                const z = orig.apply(this, a);
                try { if (z && z.__target === undefined) z.__target = targetOf(a); } catch (e) { /* */ }
                return z;
            };
        };
        // the closed exit first: createDoorZone etc. return what it made, already tagged
        const origClosed = P.createClosedExit;
        P.createClosedExit = function (r, target) { const z = origClosed.call(this, r, target); z.__target = target; z.__closed = true; return z; };
        wrap('createTransitionZone', a => a[5]);
        wrap('createDoorZone', a => a[1]?.target);
        wrap('createPathZone', a => a[1]?.target);
    }

    function exitsOf(s) { return s.children.list.filter(o => o.__target !== undefined); }
    function auditExits(s) {
        for (const z of exitsOf(s)) {
            let lbl = '';
            try { lbl = z.exitLabel ? z.exitLabel() : z.destinationName; } catch (e) { lbl = `(exitLabel threw ${e.message})`; }
            auditText(lbl, `${s.scene.key}:exit>${z.__target}${z.__closed ? '(closed)' : ''}`);
        }
    }
    /** visible texts in the active scenes (HUD, labels, panels) */
    function auditScreen() {
        for (const sc of game.scene.getScenes(true)) {
            const visit = (list, vis) => {
                for (const o of list) {
                    if (o === sc.dialogBox) continue;   // (the dialog is audited on its own, with its state)
                    const v = vis && o.visible !== false && (o.alpha ?? 1) > 0.05;
                    if (o.type === 'Text' && v) auditText(o.text, `${sc.scene.key}:text`);
                    if (o.list) visit(o.list, v);
                }
            };
            visit(sc.children.list, true);
        }
    }

    async function arrive(target) {
        await wait(1.2);
        const s = cur();
        if (s?.scene.key !== target) { fail(`expected to be in ${target}, am in ${s?.scene.key}`); return s; }
        auditExits(s);
        auditScreen();
        const trip = game.registry.get('activeDrugEffect');
        if (trip) log(`  (an Oltrac trip is on: ${trip.id}, ${Math.round((Date.now() - trip.startTime) / 1000)} s since it was taken; spores ${spores()})`);
        return s;
    }

    async function rescueEnter(target) {
        rescue(`enter(${target}) directly`);
        await enter(target);
        return arrive(target);
    }

    /** Leave the current scene by its exit to `target` (a real click on the exit), wait for the next scene. */
    async function go(target, { timeout = 45 } = {}) {
        let s = cur();
        const from = s?.scene.key;
        if (s?.dialogVisible) await closeDlg();
        if (s?.shopSystem?.isOpen) s.shopSystem.close();
        await wait(0.2);
        const zones = exitsOf(s).filter(z => z.__target === target);
        const open = zones.filter(z => !z.__closed && z.input?.enabled && z.active);
        if (!open.length) {
            fail(`no open exit ${from} -> ${target}${zones.length ? ' (only a closed one: traffic cone)' : ''}; exits here: ${exitsOf(s).map(z => z.__target + (z.__closed ? '(closed)' : '')).join(', ')}`);
            return rescueEnter(target);
        }
        const tgt = game.scene.getScene(target);
        let created = false;
        const onC = () => { created = true; };
        tgt.events.once('create', onC);
        const how = await clickObj(open[0], `exit ${from} -> ${target}`);
        try {
            await until(() => created && game.scene.isActive(target), timeout * 60, `${from} -> ${target}`);
        } catch (e) {
            tgt.events.off('create', onC);
            fail(`walking ${from} -> ${target} did not change the scene in ${timeout}s (isTransitioning=${cur()?.isTransitioning}, scene=${cur()?.scene.key})`);
            return rescueEnter(target);
        }
        log(`  ${from} -> ${target}${how === 'emit' ? ' (emitted click)' : ''}`);
        return arrive(target);
    }

    // ------------------------------------------------------------------ dialogs
    async function talk(obj, expectState, what) {
        let s = cur();
        if (s.dialogVisible) await closeDlg();
        await clickObj(obj, what);
        await wait(0.4);
        s = cur();
        return check(s.dialogVisible && (!expectState || s.dialogState === expectState), `${what}: '${expectState}' opens`,
            `visible=${s.dialogVisible} state='${s.dialogState}'`);
    }
    /** Pick the option with this key (or one of these keys) in the open dialog. */
    async function pick(key, expectState) {
        const s = cur();
        const keys = Array.isArray(key) ? key : [key];
        if (!s?.dialogVisible || !s._dialogModel) { fail(`pick '${keys.join('|')}': no dialog open (last state '${s?.dialogState}')`); return false; }
        const state = s.dialogState;
        const raw = rawOptions(s, state);
        let idx = -1;
        for (const k of keys) { idx = raw.findIndex(o => o.key === k); if (idx >= 0) break; }
        const m = s._dialogModel;
        if (idx < 0 || !m.options[idx]) {
            fail(`[${s.scene.key}.${state}] option '${keys.join('|')}' not offered; offered: ${raw.map(o => o.key).join(', ') || '(none)'}`);
            return false;
        }
        const opt = m.options[idx];
        log(`  > ${s.scene.key}.${state}: "${String(opt.label).slice(0, 70)}"`);
        try { opt.activate(); } catch (e) { fail(`option '${raw[idx].key}' threw: ${e.stack || e}`); return false; }
        await wait(0.3);
        if (expectState !== undefined) {
            const t = cur();
            const ok = expectState === null ? !t.dialogVisible : (t.dialogVisible && t.dialogState === expectState);
            if (!ok) { fail(`after '${raw[idx].key}': expected ${expectState === null ? 'the dialog closed' : `'${expectState}'`}, got visible=${t.dialogVisible} state='${t.dialogState}'`); return false; }
        }
        return true;
    }
    async function pickIndex(i) {
        const s = cur();
        const raw = rawOptions(s, s.dialogState);
        if (!raw[i]) { fail(`[${s.scene.key}.${s.dialogState}] no option #${i}`); return false; }
        return pick(raw[i].key);
    }
    /** Close the dialog with its Leave / X (or hideDialog when the state hides them). */
    async function closeDlg() {
        const s = cur();
        if (!s?.dialogVisible) return;
        const close = s._dialogModel?.options?.find(o => o.isClose);
        if (close) close.activate(); else s.hideDialog();
        await wait(0.3);
    }
    /** Show a state directly (a rescue when an option the route needs is missing). */
    async function force(state) {
        rescue(`showDialog('${state}') directly`);
        cur().showDialog(state);
        await wait(0.3);
    }
    async function pickOr(key, expectState) {
        if (await pick(key, expectState)) return true;
        if (expectState) await force(expectState);
        return false;
    }

    /** One beat: its own name in the log, an exception fails it without stopping the run. */
    let loopDead = false;
    /** Phaser's loop stops for good when a step throws (its rAF isn't requested again): nothing moves any more */
    async function loopAlive() {
        const f = game.loop.frame;
        await frame(false); await frame(false); await frame(false);
        return game.loop.frame > f;
    }
    async function step(name, fn) {
        beat = name;
        if (loopDead) { log(`--- ${name} --- SKIPPED (the game loop is dead)`); return; }
        log(`--- ${name} ---`);
        try { await fn(); } catch (e) { fail(`threw: ${e.stack || e}`); }
        if (!await loopAlive()) {
            loopDead = true;
            const last = consoleLog.filter(c => c.lvl !== 'warn').slice(-1)[0];
            fail(`THE GAME FROZE: Phaser's loop stopped during '${name}' (an exception inside a game step${last ? ': ' + last.msg.split('\n').slice(0, 3).join(' | ') : ''}). The rest of the route can't run.`);
            await still(`frozen_${name.replace(/[^a-z0-9]+/gi, '_')}`);
        }
    }
    /** A key press as the keyboard sends it (Phaser reads keyCode, which a synthetic KeyboardEvent can't set itself). */
    async function pressKey(key, keyCode) {
        for (const type of ['keydown', 'keyup']) {
            const e = new KeyboardEvent(type, { key, code: `Key${key.toUpperCase()}`, bubbles: true, cancelable: true });
            Object.defineProperty(e, 'keyCode', { get: () => keyCode });
            Object.defineProperty(e, 'which', { get: () => keyCode });
            window.dispatchEvent(e);
            await frame(false);
        }
    }

    function findObj(s, pred) {
        let hit = null;
        const visit = (list) => { for (const o of list) { if (!hit && pred(o)) hit = o; if (o.list) visit(o.list); } };
        visit(s.children.list);
        return hit;
    }

    async function shopBuy(itemId) {
        const s = cur();
        const shop = s.shopSystem;
        if (!shop) { fail(`no shop in ${s.scene.key}`); return false; }
        const item = (shop.listedItems?.() || shop.inventory || []).find(i => i.id === itemId);
        if (!item) { fail(`shop ${s.scene.key}: '${itemId}' not on sale (has ${(shop.listedItems?.() || shop.inventory || []).map(i => i.id).join(', ')})`); return false; }
        const before = money();
        shop.buyItem(item, shop.priceOf(item));
        await wait(0.3);
        return check(hasItem(itemId), `bought ${itemId} (${before} -> ${money()} dinar)`);
    }
    /** A finished quest feeds the spores: +10 with a notice, nothing said when they were already full. */
    function questSporesCheck(before, n0) {
        const shown = noticesSince(n0, 'notifications.questSpores');
        const want = Math.min(100, before + 10) - before;
        if (want > 0) check(spores() === before + want && shown.length === 1 && shown[0].text.includes(`+${want}`),
            `quest reward: +${want} spores with the notice (${before} -> ${spores()}; "${shown[0]?.text ?? 'no notice'}")`);
        else check(spores() === before && shown.length === 0, `quest reward: spores full (${before}), no notice`, shown.map(n => n.text).join(' | '));
    }
    function useFromBag(itemId) {
        const s = cur();
        const i = inv().findIndex(it => it.id === itemId);
        if (i < 0) { fail(`no ${itemId} in the bag`); return false; }
        s.inventorySystem.useItem(i);
        return true;
    }

    // ================================================================== the run
    log(`playthrough: lang=${LANG} branch=${BRANCH} demo=${!!(await import('../../../config/build.js')).DEMO_BUILD}`);

    await step('menu', async () => {
        await until(() => game.scene.isActive('MainScene') && game.scene.getScene('MainScene').mainNav, 120 * 60, 'MainScene');
        await wait(1);
        auditScreen();
        await still('menu');
        check(L.getLanguage() === LANG, `UI language is ${LANG}`, L.getLanguage());
        game.scene.getScene('MainScene').startNewGame();   // the "New game" entry's action
        await until(() => game.scene.isActive('IntroScene'), 20 * 60, 'IntroScene');
        pass('New game -> IntroScene');
    });

    await step('intro', async () => {
        await wait(3);
        auditScreen();
        await still('intro');
        // click through the cutscene as a player would (each click: finish the line / next line)
        let clicks = 0;
        while (game.scene.isActive('IntroScene') && clicks < 400) {
            await domClick(530, 300);
            clicks++;
            if (clicks % 6 === 0) auditScreen();
            await wait(0.5);
        }
        check(!game.scene.isActive('IntroScene'), `intro clicked through (${clicks} clicks)`);
        if (game.scene.isActive('IntroScene')) { rescue('IntroScene.skip()'); game.scene.getScene('IntroScene').skip(); }
        await until(() => game.scene.isActive('TransitionScene') || game.scene.isActive('EntryScene'), 20 * 60, 'TransitionScene');
        await wait(2.5);
        auditScreen();
        await until(() => game.scene.isActive('EntryScene'), 30 * 60, 'EntryScene');
        pass('Intro -> TransitionScene -> EntryScene');
    });

    await step('thaal', async () => {
        await until(() => cur()?.scene.key === 'EntryScene' && cur().dialogVisible, 20 * 60, "Thaal's greeting");
        const s = cur();
        check(s.dialogState === 'main', "Thaal's greeting opens by itself", s.dialogState);
        check(!!quest('find_bishop'), "quest 'find_bishop' started");
        check(hasJ('fungal_master') && hasJ('obazoba_cult'), 'journal: Thaal + the cult');
        await still('thaal');
        await pick('what_task_master', 'task');
        await pick('wait_do_you_mean_the_task_you_have_been_given_by_t', 'whyNot');
        await pick('what_should_i_tell_the_bishop_when_i_find_her', 'tellBishop');
        await pick('ill_be_on_my_way', 'farewell');
        await pick('glory_to_the_eternal_mushroom', 'tutorialOffer');
        if (BRANCH === 'tutorial') {
            await pick('tutorial_yes', null);
            await equipmentTutorial();
        } else {
            await pick('tutorial_no', 'close');
            await closeDlg();
            check(!cur().dialogVisible, 'the talk with Thaal can be closed');
        }
        await wait(11);
        check(!cur().master?.active, 'Thaal walked off');
    });

    // ------------------------------------------------------------------ Thaal's equipment tutorial (utils/equipmentTutorial.js)
    /** Visible texts with exactly this label in any running scene (the caption moves into the panel's scene). */
    function textsLabelled(label) {
        const out = [];
        for (const sc of game.scene.getScenes(true)) {
            const visit = (list, vis) => {
                for (const o of list) {
                    const v = vis && o.visible !== false && (o.alpha ?? 1) > 0.05;
                    if (o.type === 'Text' && v && o.text === label) out.push({ o, sc });
                    if (o.list) visit(o.list, v);
                }
            };
            visit(sc.children.list, true);
        }
        return out;
    }
    /** Click a tutorial caption button (a Rectangle under its label, in a container) like a player. */
    async function clickCaptionButton(label) {
        const hit = textsLabelled(label)[0];
        if (!hit) return false;
        const t = hit.o, c = t.parentContainer;
        const rect = c?.list.find(o => o.type === 'Rectangle' && o.input?.enabled && Math.abs(o.x - t.x) < 2 && Math.abs(o.y - t.y) < 2);
        if (!rect) { fail(`tutorial: no button under "${label}"`); return false; }
        let fired = false;
        rect.once('pointerdown', () => { fired = true; });
        await domClick(c.x + rect.x, c.y + rect.y);
        if (!fired) {
            warn(`tutorial: a real click on "${label}" (${Math.round(c.x + rect.x)},${Math.round(c.y + rect.y)} in ${hit.sc.scene.key}) didn't reach it; emitting`);
            rect.emit('pointerdown');
        }
        log(`  [tutorial] "${label}"`);
        await wait(0.6);
        return true;
    }
    async function equipmentTutorial() {
        beat = 'tutorial';
        const s = cur();
        const T = (en, cz) => (CS ? cz : en);
        const NEXT = T('Next ▸', 'Další ▸'), CLOSE = T('Close & continue ▸', 'Zavřít a dál ▸'), DONE = T('Done', 'Hotovo'), SKIP = T('Skip tutorial', 'Přeskočit výuku');
        let finished = false;
        s.events.once('equipment-tutorial-finished', () => { finished = true; });
        try { await until(() => s._tutorialActive, 3 * 60, 'the tutorial'); pass('"Yes please, Master." starts the equipment tutorial'); }
        catch (e) { fail('the tutorial did not start'); return; }
        await wait(0.6);
        await still('tutorial_first');
        // the panels the player opens himself, in the tutorial's order: the HUD icon (a real click) and how to tell it opened
        const panels = [
            ['journal', () => !!s.journalUI?.visible],
            ['quests', () => !!s.questLog?.questPanel?.visible],
            ['map', () => !!s.mapUI?.visible],
            ['inventory', () => !!s.inventorySystem?.inventoryVisible || !!s.inventorySystem?.inventoryPanel?.visible],
        ];
        let p = 0, nexts = 0, closes = 0;
        for (let guard = 0; guard < 30 && !finished; guard++) {
            auditScreen();
            if (await clickCaptionButton(DONE)) { await wait(0.5); break; }
            if (await clickCaptionButton(CLOSE)) { closes++; continue; }
            if (await clickCaptionButton(NEXT)) { nexts++; continue; }
            // only "Skip tutorial" on the caption: the ring wants a panel opened from the HUD
            const [icon, isOpen] = panels[p] || [];
            const skipShown = textsLabelled(SKIP).length > 0;
            if (!icon) {
                // every panel has been shown: the closing words and their "Done" should be on screen now
                const ov = game.scene.getScene('PaperScreenScene');
                fail(`tutorial: after the last panel no caption is left on screen (no "${DONE}", no "${SKIP}"); still active=${s._tutorialActive}, PaperScreenScene status=${ov?.sys.settings.status}`);
                await still('tutorial_stuck');
                break;
            }
            check(skipShown, `tutorial: the ${icon} step shows its caption ("${SKIP}")`);
            if (!skipShown && p === 1) await still('tutorial_no_caption');
            const { x, y } = hudButtonPos(s, icon);
            await domClick(x, y - 6);
            await wait(0.8);
            check(isOpen(), `tutorial: the ${icon} opens from its HUD icon`);
            if (p === 0 || icon === 'inventory') { auditScreen(); await still(`tutorial_${icon}`); }
            p++;
        }
        check(finished, `the tutorial runs to "${DONE}" (${p} panels opened, ${closes} closed, ${nexts} × "${NEXT}")`);
        if (!finished && s._tutorialActive) {
            // stuck: no button left to press. Finish it the way its finish() does, so the rest of the route can run.
            rescue('the tutorial has no button left: finishing it by hand (registry flag, lock off, the finished event)');
            [s.journalUI?.visible && (() => s.journalUI.toggle()), s.inventorySystem?.inventoryVisible && (() => s.inventorySystem.toggleInventory(false))].forEach(f => f && f());
            s._tutorialActive = false;
            game.registry.set('equipment_tutorial_done', true);
            s.playerMovementSystem?.setDialogVisible(false);
            s.events.emit('equipment-tutorial-finished');
            await wait(0.5);
        }
        check(p === 4 && closes === 4 && nexts === 3, 'all 8 tutorial steps were shown');
        check(game.registry.get('equipment_tutorial_done') === true && !s._tutorialActive, 'equipment_tutorial_done; the tutorial lock is released');
        check(!s.journalUI?.visible && !s.mapUI?.visible && !s.questLog?.questPanel?.visible && !s.inventorySystem?.inventoryVisible, 'no panel left open');
        check(!s.isInputBlocked(), 'input is free again');
        beat = 'thaal';
    }

    await step('cathedral', async () => {
        await go('EggCatedralScene');
        let s = await go('CathedralEntrance');
        await talk(s.templeGuard, 'templeGuardGreeting', 'Temple Guard');
        check(hasUpd('find_bishop', 'guard_cathedral_closed'), 'find_bishop: guard_cathedral_closed');
        await pick('where_can_i_find_the_bishop', 'bishop_info');
        check(hasUpd('find_bishop', 'guard_bishop_not_inside'), 'find_bishop: guard_bishop_not_inside');
        await pick('what_is_the_voxmarket', 'templeGuardVoxmarket');
        await pick('what_is_the_shed_521', 'templeGuardShed521');
        await still('guard');
        await closeDlg();
        await go('EggCatedralScene');
        await go('CrossroadScene');
    });

    if (BRANCH === 'skyship') await skyshipBranch();
    else if (BRANCH === 'alt') await altBranch();
    else if (BRANCH === 'button') await buttonBranch();
    else if (BRANCH === 'tutorial') await ortolanFormRoute('deformity');      // the tutorial ran with Thaal above
    else if (BRANCH === 'dispensation' || BRANCH === 'temporary') await ortolanFormRoute(BRANCH);
    else if (BRANCH === 'firstkey') await firstPanelByKey();
    else if (BRANCH === 'firstzerren') await firstPanelZerren();
    else await mainBranch();

    // ================================================================== branch: Thorne-Still + all side quests
    async function mainBranch() {
        await step('corpse:thorne-still', async () => {
            const s = cur();
            await talk(s.corpse, 'corpseMain', 'the corpse');
            await pick('cut_it_open', 'acceptSymbiont');
            check(hasJ('symbiont_thorne_still_offered'), 'journal: Thorne-Still offered');
            await pick('accept_thornestill_as_your_symbiont', 'acceptSymbiontConfirm');
            await pick('continue', null);
            check(symbionts()?.hasSymbiont('thorne-still'), 'Thorne-Still bonded');
            check(hasJ('symbiont_thorne_still_accepted'), 'journal: Thorne-Still accepted');
            await wait(1);
            await still('thorne_still');
            await talk(s.corpse, 'corpseExhausted', 'the corpse again');
            check(!rawOptions(s, 'corpseExhausted').some(o => /plant/.test(o.key)), 'the corpse is used up: no spores into it (the skyship is lost, by design)');
            await closeDlg();
        });

        await step('kloor:deal', async () => {
            const s = await go('VoxMarket');
            await talk(s.kloor, 'kloor_start', 'Kloor Venn');
            check(hasJ('kloor_venn_meeting'), 'journal: Kloor');
            await pick('do_you_know_anything_about_the_bishop', 'kloor_bishop');
            await pick('what_was_she_trading', 'kloor_bishop_trading');
            await pick('tell_me_more_about_these_vestigels', 'kloor_vestigels');
            await pick('i_could_help_you_get_one', 'kloor_vestigels_help');
            await pick('deal', 'kloor_vestigels_quest_start');
            check(!!quest('the_three_vestigels'), "quest 'the_three_vestigels' started");
            check(hasUpd('find_bishop', 'vestigel'), 'find_bishop: vestigel');
            check(!!cur().questLog?.questNotificationIndicator?.visible, "the quest button's badge lights up in the scene the player is in");
            await pick('ok', 'kloor_vestigels_quest_info');
            await still('kloor');
            await pick('ill_find_one_for_you', null);
        });

        await step('zerren:brain-rot', async () => {
            const s = await go('VoxmarketMarketScene');
            await talk(s.zerren, 'zerren_start', 'Zerren');
            await pick('about_the_vestigel_you_had', 'zerren_vestigel_inquiry');
            await pick('kloor_told_me_about_it', 'zerren_kloor_inquiry');
            check(hasUpd('the_three_vestigels', 'vestigel_in_toy'), 'the_three_vestigels: vestigel_in_toy');
            await pick('who_did_you_sell_it_to', 'zerren_buyer_inquiry');
            const sp = spores();
            const rot = rawOptions(s, 'zerren_buyer_inquiry').some(o => o.key === 'use_thornestills_brain_rot_power');
            check(rot, `Thorne-Still's Brain Rot offered (decay ${game.registry.get('growthDecaySystem')?.getDecay?.()}, spores ${sp})`);
            if (rot) {
                await pick('use_thornestills_brain_rot_power', 'zerren_thorne_still_power');
                check(spores() === sp - 10, `Brain Rot costs 10 spores (${sp} -> ${spores()})`);
                await pick('who_bought_the_plush_toy', 'zerren_thorne_still_success');
                await pick('thank_you_for_your_help_maybe_take_some_rest_you_d', 'zerren_quest_update');
            } else {
                await pick('offer_50_dinar_as_incentive', 'zerren_bribe_attempt');
                await pick('confirm', 'zerren_bribe_success');
                await pick('thank_you_for_the_information', 'zerren_quest_update');
            }
            check(hasUpd('the_three_vestigels', 'found_eskola_lead'), 'the_three_vestigels: found_eskola_lead (Edgar)');
            await pick('leave', null);
        });

        await step('edgar:book', async () => {
            await go('VoxMarket');
            await go('CrossroadScene');
            await go('ScraperScene');
            await go('BurningBearStreetScene');
            const s = await go('ScreamingCorkScene');
            await talk(s.edgar, 'edgar_start', 'Edgar Eskola');
            check(hasJ('edgar_eskola_meeting'), 'journal: Edgar');
            await pick('im_looking_for_a_vestigel_i_heard_you_might_have_o', 'edgar_vestigel');
            await pick('i_need_it_for_an_important_purpose', 'edgar_vestigel_need');
            await pick('what_do_you_need', 'edgar_vestigel_convince');
            await pick('maybe_i_could_help_you_with_something', 'edgar_vestigel_offer');
            check(!!quest('edgar_book'), "quest 'edgar_book' started");
            await pick('ill_do_my_best', 'edgar_vestigel_thanks');
            check(hasUpd('the_three_vestigels', 'edgar_book_trade'), 'the_three_vestigels: edgar_book_trade');
            await pick('lets_start_right_away', 'edgar_book_topics');
            for (let i = 0; i < 4 && cur().dialogState === 'edgar_book_topics'; i++) {
                await pickIndex(0);
                const next = rawOptions(cur(), cur().dialogState).map(o => o.key);
                if (next.includes('i_think_we_have_enough_topics')) { await pick('i_think_we_have_enough_topics', 'edgar_book_tone'); break; }
                await pick('lets_continue', 'edgar_book_topics');
            }
            check(cur().dialogState === 'edgar_book_tone', `topics picked: ${(game.registry.get('edgarBookDraft')?.topics || []).join(', ')}`);
            await pick('comical_finding_humor_in_the_strange', 'edgar_book_tone_selected');
            await pick('now_lets_choose_a_genre_for_the_book', 'edgar_book_genre');
            await pick('funny_animals_with_depression', 'edgar_book_genre_selected');
            await pick('lets_decide_on_the_main_protagonist', 'edgar_book_protagonist');
            await pick('a_dream_detective', 'edgar_book_protagonist_selected');
            await pick('finally_lets_choose_a_setting', 'edgar_book_setting');
            await pick('the_graveyard_of_dead_gods', 'edgar_book_setting_selected');
            const sp = spores(), n0 = notices.length;
            await pick('lets_see_what_book_weve_created', 'edgar_book_completion');
            check(qDone('edgar_book'), "quest 'edgar_book' complete");
            check(hasJ('edgar_book_completed'), 'journal: the book');
            questSporesCheck(sp, n0);
            await still('edgar_book');
            await pick('read_the_opening', 'edgar_book_excerpt_opening');
            await pick('and_then', 'edgar_book_excerpt_middle');
            await pick('how_does_it_end', 'edgar_book_excerpt_ending');
            await pick('i_look_forward_to_reading_it', 'edgar_book_farewell');
            check(hasItem('vestigel'), "Edgar's Vestigel in the bag");
            check(hasUpd('the_three_vestigels', 'edgar_vestigel_acquired'), 'the_three_vestigels: edgar_vestigel_acquired');
            await pick('good_luck_edgar', null);
        });

        await step('cork:pliers', async () => {
            let s = await go('ScreamingCorkInteriorScene');
            await talk(s.heliodor, 'heliodor_start', 'Heliodor');
            await pick('do_you_have_anything_for_sale', 'heliodorMerchandise');
            await pick('show_me_what_you_have_for_sale', 'openShop');
            await pick('open_shop_interface');
            await wait(0.8);
            s = cur();
            check(!!s.shopSystem?.isOpen && !!paperOpen(), "Heliodor's shop opens (on screen)");
            auditScreen();
            await still('cork_shop');
            await shopBuy('pliers');
            s.shopSystem?.close();
            await wait(0.5);
        });

        await step('gnur:quest', async () => {
            await go('ScreamingCorkScene');
            await go('BurningBearStreetScene');
            await go('ScraperScene');
            await go('CrossroadScene');
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur');
            check(hasJ('gnur_meeting'), 'journal: Gnur');
            await pick('im_looking_for_the_bishop_have_you_seen_her', 'bishop');
            await pick('what_do_you_want', 'rustReclamation');
            await pick('ok_tell_me_more', 'recoverTech');
            check(!!quest('rust_reclamation'), "quest 'rust_reclamation' started");
            await still('gnur');
            await closeDlg();
        });

        await step('hall:living-core', async () => {
            await go('Shed521FloorsScene');
            await go('ShedAbandonedOfficeScene');
            const s = await go('ShedHallScene');
            await talk(s._livingCore, 'main', 'the Living Core');
            await pick('use_pliers_to_carefully_extract_it', 'careful_extract');
            check(hasItem('living-core'), 'Living Core in the bag');
            check(hasUpd('rust_reclamation', 'core_taken_careful'), 'rust_reclamation: core_taken_careful');
            await pick('continue', 'careful_extract_complete');
            await pick('continue', 'goodbye_taken');
            await closeDlg();
        });

        await step('gnur:deliver', async () => {
            await go('ShedAbandonedOfficeScene');
            await go('Shed521FloorsScene');
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur (with the core)');
            const m0 = money(), sp = spores(), n0 = notices.length;
            await pick('i_have_the_living_core_you_wanted', 'complete_quest');
            await pick('thank_you_for_the_information', 'complete_quest_end');
            check(money() === m0 + 30, `Gnur pays 30 dinar for the core (${m0} -> ${money()})`);
            questSporesCheck(sp, n0);
            check(qDone('rust_reclamation') && hasUpd('rust_reclamation', 'core_delivered'), 'rust_reclamation complete (core_delivered)');
            check(!hasItem('living-core'), 'the core left the bag');
            check(quest('find_bishop')?.updates?.some(u => /^bishop_l/.test(u.key)), "find_bishop: Gnur's story of the Bishop going to Dr. Elphi");
            await pick('leave', null);
        });

        await step('ortolan:start', async () => {
            await go('Shed521FloorsScene');
            await go('Shed521GateScene');
            const s = await go('ShedCourtyard');
            await talk(s._ortolan, 'main', 'Ortolan');
            check(hasJ('ortolan_meeting'), 'journal: Ortolan');
            await pick('why_do_you_need_extra_arms', 'explain_need');
            await pick('i_could_help_you_with_the_application_process', 'start_quest');
            check(!!quest('ortolan_arms'), "quest 'ortolan_arms' started");
            await pick('ill_see_what_i_can_do', 'accept_quest');
            await still('ortolan');
            await pick('ill_do_my_best', null);
        });

        await step('ortolan:applications', async () => {
            await go('Shed521GateScene');
            await go('Shed521FloorsScene');
            const s = await go('ShedApplicationsScene');
            await talk(s.clerk, 'start', 'the Applications clerk');
            await pick('how_can_i_register_for_extra_pair_of_arms', 'ortolan_inquiry');
            await pick('my_friend_needs_them_hes_an_artisan', 'ortolan_artisan');
            await pick('can_it_be_renewed', 'ortolan_renew');
            check(hasUpd('ortolan_arms', 'artisan_form_clue'), 'ortolan_arms: artisan_form_clue');
            await pick('back_to_other_topics', 'start');
            await closeDlg();
        });

        await step('ortolan:registration', async () => {
            await go('Shed521FloorsScene');
            let s = await go('ShedRegistrationScene');
            await wait(5);   // the dream queue fades in
            await still('dream_queue');
            await talk(s.sleeplessMime, 'sleeplessMime_start', 'the Sleepless Mime');
            await pick('err_i_am_at_the_right_place_can_you_help_my_friend', 'sleeplessMime_ortolan');
            await pick('read_the_fragment', 'sleeplessMime_rulebook');
            check(hasItem('rulebook-fragment'), 'rulebook fragment in the bag');
            await pick('err_thank_you_i_guess', 'sleeplessMime_end');
            await pick('continue_waiting', null);
            await wait(2);
            await talk(s.hollowWoman, 'hollowWoman_start', 'the Hollow Woman');
            await pick('do_you_remember_what_you_have_waited_for', 'hollowWoman_hands');
            await pick('ill_remember_sure_thank_you_ehm_strange_waiting_pe', 'hollowWoman_end');
            await pick('continue_waiting', null);
            await wait(2);
            await talk(s.vowelSeller, 'vowelSeller_start', 'the Vowel Seller');
            await pick('ill_buy_one', 'vowelSeller_buy');
            await pick('thank_you_but_you_know_we_have_no_names_i_am_just_', 'vowelSeller_end');
            await pick('continue_waiting', null);
            await wait(5);   // the queue fades, the Senior Clerk steps up
            s = cur();
            check(hasJ('dream_queue_completed'), 'the dream queue is done');
            check(!!s.seniorClerk?.visible && s.seniorClerk.alpha > 0.9 && !!s.seniorClerk.input?.enabled, 'the Senior Clerk appeared');
            await talk(s.seniorClerk, 'seniorClerk_start', 'the Senior Clerk');
            await pick('i_need_to_register_for', 'seniorClerk_register');
            await pick('thank_you', 'seniorClerk_processing');
            await pick('proceed_to_the_registration_office', 'registration_start');
            await pick('i_need_an_artisans_exemption_form', 'registration_artisan');
            await pick('its_for_ortolan_a_board_game_designer', 'registration_artisan_ortolan');
            await pick('i_can_demonstrate_my_creativity', 'registration_creative_challenge');
            await pick('show_the_rulebook_fragment', 'registration_success_artisan');
            check(hasItem('artisan-exemption-form'), "Artisan's Exemption Form in the bag");
            await pick('thank_you', 'registration_complete_success');
            await pick('thank_you', null);
        });

        await step('ortolan:reward', async () => {
            await go('Shed521FloorsScene');
            await go('Shed521GateScene');
            const s = await go('ShedCourtyard');
            const before = new Set(inv().map(i => i.id));
            await talk(s._ortolan, 'quest_active', 'Ortolan (with the form)');
            await pick('i_have_an_artisans_exemption_form_for_you', 'give_artisan_form');
            await pick('happy_to_help', 'complete_quest_artisan');
            check(qDone('ortolan_arms'), "quest 'ortolan_arms' complete");
            const gift = inv().filter(i => !before.has(i.id)).map(i => i.id);
            check(gift.length > 0 && !hasItem('artisan-exemption-form'), `Ortolan's gift: ${gift.join(', ') || 'none'}`);
            await still('ortolan_gift');
            await pick('thank_you_ill_treasure_it', 'quest_completed');
            await pick('ill_look_forward_to_it', null);
        });

        await step('kloor:vestigel', async () => {
            await go('Shed521GateScene');
            await go('Shed521FloorsScene');
            await go('Shed521Scene');
            await go('CrossroadScene');
            const s = await go('VoxMarket');
            await talk(s.kloor, 'kloor_start', 'Kloor Venn (with the Vestigel)');
            const m0 = money(), sp = spores(), n0 = notices.length;
            await pick('i_have_a_vestigel_for_you', 'kloor_vestigels_complete');
            check(money() === m0 + 20, `Kloor pays 20 dinar for the Vestigel (${m0} -> ${money()})`);
            questSporesCheck(sp, n0);
            check(qDone('the_three_vestigels'), "quest 'the_three_vestigels' complete");
            check(!hasItem('vestigel'), 'the Vestigel left the bag');
            check(hasUpd('find_bishop', 'elphi_contact'), 'find_bishop: elphi_contact');
            await pick('tell_me', 'kloor_bishop_reveal');
            await pick('the_dream_games', 'kloor_dream_games');
            await pick('thank_you_for_the_information', null);
        });

        await step('zerren:button', async () => {
            await go('VoxmarketMarketScene');
            check(hasJ('forgotten_elevator_button_available'), "Zerren's lift button is up for sale once a Bishop story is known");
            check(money() >= 75, `the main route earns enough for the button by now (${money()} of 75 dinar)`);
            await go('VoxMarket');
        });

        await step('lift-mother:two-stories', async () => {
            await go('CrossroadScene');
            await go('ScraperScene');
            const s = await go('ScraperInteriorScene');
            await talk(s.elevator, 'lift_mother_start', 'the Lift-Mother');
            check(hasJ('lift_mother_meeting'), 'journal: the Lift-Mother');
            await pick('i_need_to_reach_dr_elphis_floor', 'lift_mother_elphi_floor');
            check(!!quest('level_177_access'), "quest 'level_177_access' started");
            await still('lift_mother');
            await pickOr('i_know_the_bishops_secret_its_important_to_reach_d', 'confession_path');
            await pick('thank_you', 'unlock_floor');
            check(hasJ('accessed_elphi_floor'), 'journal: floor 177-Quiet open');
            await pick('thank_you', 'goto_elphi_floor');
            await pick('step_out');
            await until(() => game.scene.isActive('ScraperAmbraScene') && cur()?.scene.key === 'ScraperAmbraScene', 20 * 60, 'the lift ride');
            await arrive('ScraperAmbraScene');
            check(qDone('level_177_access'), "quest 'level_177_access' complete");
            check(hasUpd('find_bishop', 'reached_elphi_studio'), 'find_bishop: reached_elphi_studio');
        });

        await step('elphi', async () => {
            const s = cur();
            const elphi = findObj(s, o => o.type === 'Container' && o.input?.enabled && Math.abs(o.x - (s.drElphi?.x ?? -1)) < 2);
            await talk(elphi, 'dr_elphi_start', 'Dr. Elphi');
            check(hasJ('met_dr_elphi'), 'journal: Dr. Elphi');
            await pick('im_looking_for_someone_the_bishop', 'dr_elphi_bishop_path');
            await pick('did_she_say_where_she_was_going', 'dr_elphi_bishop_destination');
            await pick('what_was_she_avoiding', 'dr_elphi_bishop_concerns');
            await pick('i_should_check_the_backyard', 'dr_elphi_exit');
            check(hasItem('scraper_backyard_key'), 'backyard key in the bag');
            check(hasUpd('find_bishop', 'check_shard_backyard'), 'find_bishop: check_shard_backyard');
            await still('elphi');
            await pick('ill_check_the_backyard', null);
        });

        await busEnding();
    }

    // ================================================================== branch: Zerren's Forgotten Elevator Button
    async function buttonBranch() {
        await step('quest-log', async () => {
            // the player looks at the quest log once (a real click on the HUD note). Besides being what players do, it
            // creates the panels' overlay scene: without one, Zerren's stall freezes the game (see --only firstzerren)
            const s = cur();
            const { x, y } = hudButtonPos(s, 'quests');
            await domClick(x, y - 6);
            await wait(0.8);
            check(!!s.questLog?.questPanel?.visible, 'the quest log opens from the HUD');
            auditScreen();
            await still('quest_log');
            await domClick(x, y - 6);
            await wait(0.6);
            if (s.questLog?.questPanel?.visible) s.questLog.hideQuestLog?.();
        });

        await step('gnur:quest', async () => {
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur');
            await pick('im_looking_for_the_bishop_have_you_seen_her', 'bishop');
            await pick('tell_me_what_i_want_to_know_or_else', 'threat');
            await pick('ok_tell_me_more', 'recoverTech');
            check(!!quest('rust_reclamation'), "quest 'rust_reclamation' started");
            await closeDlg();
        });

        await step('hall:force', async () => {
            await go('Shed521FloorsScene');
            await go('ShedAbandonedOfficeScene');
            const s = await go('ShedHallScene');
            await talk(s._livingCore, 'main', 'the Living Core');
            await pick('examine_it_more_carefully', 'examine');
            await pick('back', 'main');
            await pick('extract_it_forcefully', 'force_extract');
            check(hasItem('living-core') && hasUpd('rust_reclamation', 'core_taken_force'), 'the core wrenched out (core_taken_force)');
            await pick('continue', 'goodbye_taken');
            await closeDlg();
            await go('ShedAbandonedOfficeScene');
            await go('ShedHallScene');
            check(!cur()._livingCore, 'the socket stays empty on a return visit');
        });

        await step('gnur:deliver', async () => {
            await go('ShedAbandonedOfficeScene');
            await go('Shed521FloorsScene');
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur (with the core)');
            const m0 = money(), sp = spores(), n0 = notices.length;
            await pick('i_have_the_living_core_you_wanted', 'complete_quest');
            await pick('thank_you_for_the_information', 'complete_quest_end');
            check(qDone('rust_reclamation') && hasUpd('rust_reclamation', 'core_delivered'), 'rust_reclamation complete (core_delivered)');
            check(money() === m0 + 30, `Gnur pays 30 dinar (${m0} -> ${money()})`);
            questSporesCheck(sp, n0);
            await pick('leave', null);
        });

        await step('zerren:button', async () => {
            await go('CrossroadScene');
            await go('VoxMarket');
            let s = await go('VoxmarketMarketScene');
            check(hasJ('forgotten_elevator_button_available') && hasUpd('find_bishop', 'found_elevator_button'), 'the button is on sale (journal + find_bishop)');
            check(money() >= 75, `enough money for it, earned in play (${money()} dinar)`);
            await talk(s.zerren, 'zerren_start', 'Zerren');
            await pick('what_do_you_sell', 'zerren_selling');
            await pick('show_me_what_you_have_for_sale', 'zerren_shop');
            check(cur()._dialogModel?.text?.length > 0, "Zerren pitches the button before opening the stall (zerren_shop 'button')");
            await pick('let_me_take_a_look');
            await wait(0.8);
            s = cur();
            check(!!s.shopSystem?.isOpen && !!paperOpen(), "Zerren's stall opens (on screen)");
            auditScreen();
            await still('zerren_button');
            const m0 = money();
            await shopBuy('forgotten_elevator_button');
            check(money() === m0 - 75, `the button costs 75 (${m0} -> ${money()})`);
            check(!!s.shopSystem?.isSoldOut?.('forgotten_elevator_button'), 'one of a kind: sold out after the purchase');
            s.shopSystem?.close();
            await wait(0.5);
            if (s.dialogVisible) await closeDlg();
            await talk(s.zerren, 'zerren_start', 'Zerren again');
            await pick('what_do_you_sell', 'zerren_selling');
            await pick('show_me_what_you_have_for_sale');
            await wait(0.8);
            check(!!cur().shopSystem?.isOpen && !!paperOpen() && !cur().dialogVisible, 'with the button sold the stall opens straight away (zerren_shop plain)');
            cur().shopSystem?.close();
            await wait(0.4);
        });

        await step('lift-mother:button', async () => {
            await go('VoxMarket');
            await go('CrossroadScene');
            await go('ScraperScene');
            const s = await go('ScraperInteriorScene');
            await talk(s.elevator, 'lift_mother_start', 'the Lift-Mother');
            await pick('i_need_to_reach_dr_elphis_floor', 'lift_mother_elphi_floor');
            const keys = rawOptions(s, 'lift_mother_elphi_floor').map(o => o.key);
            check(!keys.includes('i_know_the_bishops_secret_its_important_to_reach_d') && !keys.includes('ive_a_tool_to_repair_your_floor_counter_perhaps_yo'),
                'only one story and no tool: the button is the only way up here', keys.join(', '));
            await still('lift_button');
            await pickOr('i_have_a_button_that_belongs_here_maybe_its_been_l', 'button_path');
            check(!hasItem('forgotten_elevator_button'), 'the button went back to the Lift-Mother');
            await pick('thank_you', 'unlock_floor');
            await pick('thank_you', 'goto_elphi_floor');
            await pick('step_out');
            await until(() => game.scene.isActive('ScraperAmbraScene') && cur()?.scene.key === 'ScraperAmbraScene', 20 * 60, 'the lift ride');
            await arrive('ScraperAmbraScene');
            check(qDone('level_177_access') && hasJ('accessed_elphi_floor'), "up on the button: level_177_access complete, floor 177-Quiet open");
        });

        await step('elphi:testing', async () => {
            const s = cur();
            const elphi = findObj(s, o => o.type === 'Container' && o.input?.enabled && Math.abs(o.x - (s.drElphi?.x ?? -1)) < 2);
            await talk(elphi, 'dr_elphi_start', 'Dr. Elphi');
            await pick('ill_explain_if_you_stop_testing_me', 'dr_elphi_testing_path');
            await pick('theres_been_a_signal_anomaly', 'dr_elphi_anomaly_path');
            await pick('im_looking_for_the_bishop', 'dr_elphi_bishop_path');
            await pick('did_she_say_where_she_was_going', 'dr_elphi_bishop_destination');
            await pick('ill_go_look_for_her_there', 'dr_elphi_exit');
            check(hasItem('scraper_backyard_key'), 'backyard key in the bag');
            await pick('ill_check_the_backyard', null);
        });

        await busEnding();
    }

    // ================================================================== the first panel of a session
    // paperKit.openPaperScreen adds its overlay scene the first time a panel opens. Opened from a timer (inside a game
    // step) Phaser only queues the add, getScene() returns null and openPaperScreen throws: the step dies, and with it the
    // whole game loop. Zerren's stall opens on such a timer. Keys (J / I / Q) and clicks are fine: firstkey checks them.
    async function firstPanelByKey() {
        await step('first panel: J', async () => {
            const s = cur();
            check(!game.scene.getScene('PaperScreenScene'), 'no panel has been opened yet this session');
            await pressKey('j', 74);
            await wait(0.8);
            check(await loopAlive(), 'the game still runs after pressing J (the tutorial: "press J")');
            check(!!s.journalUI?.visible, 'J opens the diary as the first panel of the session');
            await still('first_panel_J');
        });
        await step('then: I, Q', async () => {
            const s = cur();
            await pressKey('j', 74); await wait(0.6);
            await pressKey('i', 73); await wait(0.8);
            check(!!s.inventorySystem?.inventoryVisible, 'I opens the inventory');
            await pressKey('i', 73); await wait(0.6);
            await pressKey('q', 81); await wait(0.8);
            check(!!s.questLog?.questPanel?.visible, 'Q opens the quest log');
            await pressKey('q', 81); await wait(0.6);
            await go('EggCatedralScene');
            check(cur()?.scene.key === 'EggCatedralScene', 'the game goes on');
        });
    }

    async function firstPanelZerren() {
        await step('first panel: Zerren', async () => {
            check(!game.scene.getScene('PaperScreenScene'), 'no panel has been opened yet this session');
            await go('VoxMarket');
            let s = await go('VoxmarketMarketScene');
            await talk(s.zerren, 'zerren_start', 'Zerren');
            await pick('what_do_you_sell', 'zerren_selling');
            await pick('show_me_what_you_have_for_sale');
            await wait(1);
            check(await loopAlive(), "the game still runs after asking for Zerren's wares (her stall opens on a 300 ms timer)");
            check(!!paperOpen(), "Zerren's stall is on screen");
            await still('first_panel_zerren');
        });
        await step('after', async () => {
            await go('VoxMarket');
            check(cur()?.scene.key === 'VoxMarket', 'the game goes on');
        });
    }
    function paperOpen() { const o = game.scene.getScene('PaperScreenScene'); return o && o.sys.isActive() ? o : null; }

    // ================================================================== Ortolan's other documents (one route each: the quest ends once)
    async function ortolanFormRoute(kind) {
        const FORM = { deformity: 'deformity-form', dispensation: 'special-dispensation', temporary: 'temporary-permit' }[kind];
        const GIFT = armsReward(FORM)?.id;

        await step(`ortolan:start`, async () => {
            await go('Shed521Scene');
            await go('Shed521FloorsScene');
            await go('Shed521GateScene');
            const s = await go('ShedCourtyard');
            await talk(s._ortolan, 'main', 'Ortolan');
            await pick('who_are_you', 'who_are_you');
            await pick('why_do_you_need_extra_arms', 'explain_need');
            await pick('i_could_help_you_with_the_application_process', 'start_quest');
            check(!!quest('ortolan_arms'), "quest 'ortolan_arms' started");
            await pick('ill_see_what_i_can_do', 'accept_quest');
            await pick('ill_do_my_best', null);
            await talk(s._ortolan, 'quest_active', 'Ortolan (nothing to give yet)');
            check(!rawOptions(s, 'quest_active').some(o => /^i_have_/.test(o.key)), 'no document to hand over yet');
            await pick('see_you_later', null);
        });

        await step(`ortolan:applications(${kind})`, async () => {
            await go('Shed521GateScene');
            await go('Shed521FloorsScene');
            const s = await go('ShedApplicationsScene');
            await talk(s.clerk, 'start', 'the Applications clerk');
            await pick('how_can_i_register_for_extra_pair_of_arms', 'ortolan_inquiry');
            if (kind === 'dispensation') {
                await pick('my_friend_needs_them_hes_an_artisan', 'ortolan_artisan');
                await pick('forget_the_form_what_else_can_i_offer', 'ortolan_offer');
                check(hasUpd('ortolan_arms', 'nonverbal_gesture_clue'), 'ortolan_arms: nonverbal_gesture_clue');
                await pick('uh_okay_can_i_ask_for_other_topics', 'start');
            } else {
                await pick('theyre_not_his_arms_hes_borrowing_them', 'ortolan_borrow');
                await pick('well_i_was_just_joking_of_course_they_are_his_but_', 'ortolan_gift');
                await pick('can_you_process_it_today', 'ortolan_today');
                check(hasUpd('ortolan_arms', 'deformity_form_clue'), 'ortolan_arms: deformity_form_clue');
                await pick('back_to_other_topics', 'start');
            }
            check(!rawOptions(s, 'start').some(o => o.key === 'how_can_i_register_for_extra_pair_of_arms'), 'the arms topic closes once a form is named');
            await closeDlg();
        });

        await step(`ortolan:registration(${kind})`, async () => {
            await go('Shed521FloorsScene');
            let s = await go('ShedRegistrationScene');
            await wait(5);
            // the queue: what the three figures leave behind decides what the Senior Clerk accepts
            await talk(s.sleeplessMime, 'sleeplessMime_start', 'the Sleepless Mime');
            await pick('hi_who_are_you_i_used_to_play_like_this_as_well_wh', 'sleeplessMime_memory');
            await pick('remember', 'sleeplessMime_memory_scene');
            await pick('thank_you_for_reminding_me', 'sleeplessMime_end');
            await pick('finally_i_hate_mimes', null);
            await wait(2);
            await talk(s.hollowWoman, 'hollowWoman_start', 'the Hollow Woman');
            if (kind === 'deformity') {
                await pick('do_you_remember_what_you_have_waited_for', 'hollowWoman_hands');
                await pick('ill_remember_sure_thank_you_ehm_strange_waiting_pe', 'hollowWoman_end');
            } else {
                await pick('well_i_guess_you_should_stop_waiting_i_am_sure_you', 'hollowWoman_offer');
                await pick('uhm_what_are_you_doing_madame', 'hollowWoman_end');
            }
            await pick('continue_waiting', null);
            await wait(2);
            await talk(s.vowelSeller, 'vowelSeller_start', 'the Vowel Seller');
            if (kind === 'dispensation') {
                await pick('keep_your_vowels_i_speak_in_spore_alphabet', 'vowelSeller_spores');
                check(hasItem('silent-sentence'), 'the Silent Sentence card in the bag');
                await pick('i_accept_this_gift', 'vowelSeller_end');
            } else {
                await pick('ill_buy_one', 'vowelSeller_buy');
                await pick('thank_you_but_you_know_we_have_no_names_i_am_just_', 'vowelSeller_end');
            }
            await pick('continue_waiting', null);
            await wait(5);
            s = cur();
            check(!!s.seniorClerk?.visible && s.seniorClerk.alpha > 0.9, 'the Senior Clerk appeared');
            await talk(s.seniorClerk, 'seniorClerk_start', 'the Senior Clerk');
            await pick('what_happened_to_those_people_i_was_talking_to', 'seniorClerk_people');
            await pick('i_see', 'seniorClerk_processing');
            await pick('proceed_to_the_registration_office', 'registration_start');
            const g0 = game.registry.get('growthDecaySystem')?.getGrowth?.();
            if (kind === 'deformity') {
                await pick('i_need_an_inherited_deformity_form', 'registration_deformity');
                await pick('its_for_a_friend_with_multiple_arms', 'registration_deformity_friend');
                await pick('recite_the_bureaucratic_incantation_to_bypass_the_', 'registration_success_deformity');
                await pick('thank_you', 'registration_complete_success');
            } else if (kind === 'temporary') {
                await pick('i_need_an_inherited_deformity_form', 'registration_deformity');
                await pick('i_need_to_understand_the_classification_system', 'registration_deformity_system');
                await pick('i_have_some_experience_with_bureaucracy', 'registration_bureaucracy_challenge');
                await pick('section_7b_covers_beneficial_mutations', 'registration_partial_success');
                check(hasUpd('ortolan_arms', 'partial_progress'), 'ortolan_arms: partial_progress');
                await pick('i_understand', 'registration_complete_partial');
            } else {
                await pick('make_a_nonverbal_gesture', 'registration_nonverbal');
                await pick('present_the_silent_sentence_card', 'registration_success_nonverbal');
                await pick('nod_gratefully', 'registration_complete_success');
            }
            check(hasItem(FORM), `the ${FORM} in the bag`);
            await still(`registration_${kind}`);
            await pick('thank_you', null);
            log(`  growth ${g0} -> ${game.registry.get('growthDecaySystem')?.getGrowth?.()}`);
            await talk(s.seniorClerk, 'registration_start', 'the Senior Clerk again');
            const keys = rawOptions(s, 'registration_start').map(o => o.key);
            check(!keys.some(k => ['i_need_an_inherited_deformity_form', 'make_a_nonverbal_gesture', 'i_need_an_artisans_exemption_form'].includes(k)),
                'the form path is closed after its one outcome', keys.join(', '));
            await closeDlg();
        });

        await step(`ortolan:gift(${kind})`, async () => {
            await go('Shed521FloorsScene');
            await go('Shed521GateScene');
            const s = await go('ShedCourtyard');
            const sp = spores(), n0 = notices.length;
            await talk(s._ortolan, 'quest_active', `Ortolan (with the ${FORM})`);
            const GIVE = { deformity: ['i_have_an_inherited_deformity_form_for_you', 'give_deformity_form', 'its_what_i_could_get', 'complete_quest_deformity', 'thank_you_for_this_gift'],
                dispensation: ['i_have_a_special_dispensation_for_you', 'give_special_dispensation', 'sometimes_actions_speak_louder_than_words', 'complete_quest_dispensation', 'its_beautiful_thank_you'],
                temporary: ['i_have_a_temporary_permit_for_you', 'give_temporary_permit', 'sorry_its_not_better', 'complete_quest_temporary', 'thank_you_for_the_figurine'] }[kind];
            await pick(GIVE[0], GIVE[1]);
            await pick(GIVE[2], GIVE[3]);
            check(qDone('ortolan_arms') && hasUpd('ortolan_arms', 'completed'), "quest 'ortolan_arms' complete");
            check(hasItem(GIFT) && !hasItem(FORM), `Ortolan's gift: ${GIFT} (the ${FORM} handed over)`);
            questSporesCheck(sp, n0);
            await wait(0.3);
            check(s.children.list.some(o => o.type === 'ParticleEmitter'), 'the completion spores burst round Ortolan');
            await still(`ortolan_gift_${kind}`);
            await pick(GIVE[4], 'quest_completed');
            await pick('tell_me_more_about_your_games', 'games_discussion');
            await pick('sounds_fascinating', null);
            await talk(s._ortolan, 'quest_completed', 'Ortolan afterwards');
            await closeDlg();
        });

        await step('after', async () => {
            // the game goes on: back out to the city, the main line still open
            await go('Shed521GateScene');
            await go('Shed521FloorsScene');
            await go('Shed521Scene');
            await go('CrossroadScene');
            check(!qDone('find_bishop'), 'the main line is still open: the run can carry on');
        });
    }

    // ================================================================== branch: the other ways (Ulvarex's weaves, no money)
    async function altBranch() {
        let tripStart = null;
        await step('corpse:decline', async () => {
            const s = cur();
            await talk(s.corpse, 'corpseMain', 'the corpse');
            await pick('cut_it_open', 'acceptSymbiont');
            await pick('decline', 'declineSymbiont');
            await pick('continue', null);
            check(hasJ('symbiont_thorne_still_declined') && !symbionts()?.hasSymbiont('thorne-still'), 'Thorne-Still declined');
            await talk(s.corpse, 'corpseReconsider', 'the corpse again (Thorne-Still waits)');
            const keys = rawOptions(s, 'corpseReconsider').map(o => o.key);
            check(keys.includes('accept_thornestill_as_your_symbiont') && keys.includes('plant_spores_in_it_instead'), 'he can still take Thorne-Still or plant spores', keys.join(', '));
            await pick('leave_it_alone', null);
        });

        await step('kloor:violet+deal', async () => {
            let s = await go('VoxMarket');
            await talk(s.kloor, 'kloor_start', 'Kloor Venn');
            await pick('what_are_you_selling', 'kloor_selling');
            await pick('show_me_what_you_have');
            await wait(0.8);
            s = cur();
            check(!!s.shopSystem?.isOpen && !!paperOpen(), "Kloor's shop opens (on screen)");
            await shopBuy('violetOltrac');
            s.shopSystem?.close();
            await wait(1.5);
            if (s.dialogVisible) { log(`  (after the shop: '${s.dialogState}')`); await closeDlg(); }
            await talk(s.kloor, 'kloor_start', 'Kloor Venn');
            await pick('do_you_know_anything_about_the_bishop', 'kloor_bishop');
            await pick('do_you_know_where_she_went', 'kloor_bishop_location');
            await pick('what_was_she_trading', 'kloor_bishop_trading');
            await pick('tell_me_more_about_these_vestigels', 'kloor_vestigels');
            await pick('sounds_dangerous', 'kloor_vestigels_dangerous');
            await pick('i_could_help_you_get_one', 'kloor_vestigels_help');
            await pick('deal', 'kloor_vestigels_quest_start');
            await pick('ok', 'kloor_vestigels_quest_info');
            await pick('ill_find_one_for_you', null);
            check(!!quest('the_three_vestigels'), "quest 'the_three_vestigels' started");
        });

        await step('ulvarex:roof', async () => {
            await go('CrossroadScene');
            const s = await go('ScraperScene');
            useFromBag('violetOltrac');
            await wait(0.5);
            try { await until(() => cur().dialogVisible && cur().dialogState === 'ulvarex_notice', 25 * 60, 'Ulvarex'); pass('Ulvarex speaks up from the rooftop puddle'); }
            catch (e) { fail(`Ulvarex did not speak up on the Scraper roof in 25 s (shown=${s._ulvarex?.shown})`); await force('ulvarex_notice'); }
            await still('ulvarex_roof');
            await pick('ulvarex_crouch', 'ulvarex_reach');
            await pick('ulvarex_why_puddle', 'ulvarex_why');
            await pick('ulvarex_what_bond', 'ulvarex_bond');
            await pick('ulvarex_bond_yes', 'ulvarex_accept');
            check(symbionts()?.hasSymbiont('ulvarex-borrowed-horizon'), 'Ulvarex bonded on the roof');
            await pick('ulvarex_welcome', null);
            await wait(2);
            log(`  spores after the bond: ${spores()}; the trip goes on while he walks about`);
            tripStart = notices.length;
        });

        await step('zerren:persuade', async () => {
            await go('CrossroadScene');
            await go('VoxMarket');
            const s = await go('VoxmarketMarketScene');
            await talk(s.zerren, 'zerren_start', 'Zerren');
            await pick('about_the_vestigel_you_had', 'zerren_vestigel_inquiry');
            await pick('i_cant_tell_you_it_doesnt_matter', 'zerren_refuse_inquiry');
            await pick('who_did_you_sell_it_to', 'zerren_buyer_inquiry');
            let tries = 0;
            for (; tries < 30; tries++) {
                if (!await pick('try_to_persuade_her', 'zerren_persuade_attempt')) break;
                await pick('continue_persuading');
                if (cur().dialogState === 'zerren_persuade_success') break;
                if (!await pick('try_something_else', 'zerren_buyer_inquiry')) break;
            }
            check(cur().dialogState === 'zerren_persuade_success', `persuasion worked (after ${tries + 1} tries; 25 % each, retries allowed)`);
            await pick('thank_you_for_understanding', 'zerren_quest_update');
            check(hasUpd('the_three_vestigels', 'found_eskola_lead'), 'the_three_vestigels: found_eskola_lead');
            await pick('leave', null);
        });

        await step('gnur:mirage', async () => {
            await go('VoxMarket');
            await go('CrossroadScene');
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur');
            await pick('im_looking_for_the_bishop_have_you_seen_her', 'bishop');
            await pick('i_can_help_you_recover_old_tech_carefully', 'recoverTech');
            check(!!quest('rust_reclamation'), "quest 'rust_reclamation' started");
            await closeDlg();
            log(`  spores: ${spores()}`);
            await talk(s.gnur, 'start', 'Gnur (waiting)');
            if (await pick('ulvarex_mirage_core', 'mirage_core_weave')) {
                await pick('mirage_core_hand_over', 'complete_quest');
                await pick('thank_you_for_the_information', 'complete_quest_mirage_end');
                check(qDone('rust_reclamation') && hasUpd('rust_reclamation', 'core_illusion'), 'rust_reclamation complete with the mirage (core_illusion)');
                await pick('leave', null);
            } else {
                warn(`no [Ulvarex] mirage for Gnur (spores ${spores()}, decay ${game.registry.get('growthDecaySystem')?.getDecay?.()})`);
                await closeDlg();
            }
        });

        await step('ortolan+clerk', async () => {
            await go('Shed521FloorsScene');
            await go('Shed521GateScene');
            let s = await go('ShedCourtyard');
            await talk(s._ortolan, 'main', 'Ortolan');
            await pick('board_games_what_do_you_mean', 'board_games');
            await pick('i_could_help_you_with_the_application_process', 'start_quest');
            await pick('ill_see_what_i_can_do', 'accept_quest');
            await pick('ill_do_my_best', null);
            await go('Shed521GateScene');
            await go('Shed521FloorsScene');
            s = await go('ShedApplicationsScene');
            await talk(s.clerk, 'start', 'the Applications clerk');
            if (hasUpd('rust_reclamation', 'core_illusion')) {
                await pick('gnur_got_a_mirage', 'core_mirage_thanks');
                check(hasUpd('find_bishop', 'bishop_elphi_clerk'), "find_bishop: the Tribunal's records after the mirage");
                await pick('thank_you_that_helps', 'start');
            }
            await pick('how_can_i_register_for_extra_pair_of_arms', 'ortolan_inquiry');
            await pick('my_friend_didnt_choose_this_the_arms_were_a_gift', 'ortolan_gift');
            await pick('fine_ill_lie_or_forge_the_documents', 'ortolan_lie');
            check(quest('ortolan_arms')?.updates?.length > 0, `ortolan_arms: ${quest('ortolan_arms')?.updates?.map(u => u.key).join(', ')}`);
            await pick('back_to_other_topics', 'start');
            await closeDlg();
        });

        await step('edgar:book-first', async () => {
            await go('Shed521FloorsScene');
            await go('Shed521Scene');
            await go('CrossroadScene');
            await go('ScraperScene');
            await go('BurningBearStreetScene');
            const s = await go('ScreamingCorkScene');
            await talk(s.edgar, 'edgar_start', 'Edgar Eskola');
            await pick('tell_me_about_yourself', 'edgar_background');
            await pick('what_would_you_like_to_do', 'edgar_dream_job');
            await pick('i_can_help_you_write_the_book', 'edgar_book');
            check(!!quest('edgar_book'), "quest 'edgar_book' started (without the Vestigel deal)");
            await pick('lets_start_with_some_inspirational_topics', 'edgar_book_topics');
            for (let i = 0; i < 4 && cur().dialogState === 'edgar_book_topics'; i++) {
                await pickIndex(0);
                const next = rawOptions(cur(), cur().dialogState).map(o => o.key);
                if (next.includes('i_think_we_have_enough_topics')) { await pick('i_think_we_have_enough_topics', 'edgar_book_tone'); break; }
                await pick('lets_continue', 'edgar_book_topics');
            }
            await pick('political_examining_power_dynamics', 'edgar_book_tone_selected');
            await pick('now_lets_choose_a_genre_for_the_book', 'edgar_book_genre');
            await pick('cosmic_horror', 'edgar_book_genre_selected');
            const sp = spores();
            if (await pick('ulvarex_edgar_villain', 'edgar_book_villain_ulvarex')) {
                check(game.registry.get('edgarBookDraft')?.villain === 'manifold' && spores() === sp - 5, `Ulvarex's villain Mr. Manifold (spores ${sp} -> ${spores()})`);
                await pick('lets_decide_on_the_main_protagonist', 'edgar_book_protagonist');
            } else await pick('lets_decide_on_the_main_protagonist', 'edgar_book_protagonist');
            if (!await pick('a_feeble_ghost', 'edgar_book_protagonist_selected')) await pick('a_rogue_ludarch', 'edgar_book_protagonist_selected');
            await pick('finally_lets_choose_a_setting', 'edgar_book_setting');
            await pick('a_skyship_above_the_clouds', 'edgar_book_setting_selected');
            await pick('lets_see_what_book_weve_created', 'edgar_book_completion');
            check(qDone('edgar_book'), "quest 'edgar_book' complete");
            await still('edgar_book_alt');
            await pick('make_sure_to_credit_me_as_coauthor', 'edgar_book_coauthor');
            await pick('read_the_opening', 'edgar_book_excerpt_opening');
            await pick('and_then', 'edgar_book_excerpt_middle');
            await pick('how_does_it_end', 'edgar_book_excerpt_ending');
            await pick('i_look_forward_to_reading_it', 'edgar_book_farewell');
            check(!hasItem('vestigel'), 'no Vestigel in the farewell without the deal');
            await pick('good_luck_edgar', null);
            await talk(s.edgar, 'edgar_start', 'Edgar again');
            await pick('im_looking_for_a_vestigel_i_heard_you_might_have_o', 'edgar_vestigel');
            await pick('may_i_have_it', 'edgar_vestigel_give_completed');
            check(hasItem('vestigel') && hasJ('edgar_vestigel_received_after_book'), "Edgar's Vestigel, asked for after the book");
            await pick('thank_you_edgar', 'edgar_start');
            check(rawOptions(s, 'edgar_start').some(o => o.key === 'read_me_from_your_book'), 'the book can be re-read');
            await closeDlg();
        });

        await step('ravla:audit', async () => {
            const s = await go('ScreamingCorkInteriorScene');
            await talk(s.ravla, 'ravla_start', 'Ravla');
            await pick('what_do_you_do_here', 'ravla_job');
            await pick('i_need_some_documents', 'ravla_documents');
            await pick('i_need_help_with_ortolans_paperwork', 'ravla_ortolan');
            await pick('what_would_you_need', 'ravla_ortolan_need');
            const canAudit = rawOptions(cur(), 'ravla_ortolan_need').some(o => o.key === 'ravla_ulvarex_audit');
            if (!canAudit) warn(`no [Ulvarex] audit at Ravla: spores ${spores()} (it costs 10)`);
            if (canAudit && await pick('ravla_ulvarex_audit', 'ravla_audit')) {
                await pick('ravla_audit_watch', 'ravla_audit_shaken');
                check(hasItem('forged-arms-permission'), 'the redone permit, free (Ulvarex\'s inspector)');
                await pick('ravla_audit_thanks', null);
            } else {
                log(`  paying Ravla 50 instead (money ${money()})`);
                await pick('heres_the_money');
                await wait(0.3);
                if (cur().dialogVisible) await closeDlg();
            }
        });

        await step('ortolan:forged', async () => {
            await go('ScreamingCorkScene');
            await go('BurningBearStreetScene');
            await go('ScraperScene');
            await go('CrossroadScene');
            await go('Shed521Scene');
            await go('Shed521FloorsScene');
            await go('Shed521GateScene');
            const s = await go('ShedCourtyard');
            if (!hasItem('forged-arms-permission')) { warn('no forged permit to bring (neither spores for the audit nor 50 dinar): Ortolan stays open on this route'); return; }
            await talk(s._ortolan, 'quest_active', 'Ortolan (with the forged permit)');
            await pick('i_have_a_forged_multiple_arms_permission_for_you', 'give_forged_permission');
            await pick('id_rather_not_say', 'forged_reaction');
            await pick('its_for_a_good_cause', 'complete_quest_forged');
            check(qDone('ortolan_arms') && hasItem('apocalypse-cop-figure'), 'ortolan_arms complete: Apocalypse Cop');
            await pick('thank_you_for_the_gift', 'quest_completed');
            await pick('you_mentioned_being_a_worldwright_what_were_the_bo', 'ortolan_board_wars');
            await pick('what_went_wrong', 'ortolan_board_wars_fall');
            await pick('how_did_it_end', 'ortolan_board_wars_end');
            check(hasJ('board_games_war'), 'journal: the Board Game Wars');
            await closeDlg();
        });

        await step('kloor:vestigel+spores', async () => {
            await go('Shed521GateScene');
            await go('Shed521FloorsScene');
            await go('Shed521Scene');
            await go('CrossroadScene');
            const s = await go('VoxMarket');
            await talk(s.kloor, 'kloor_start', 'Kloor Venn');
            await pick('i_have_a_vestigel_for_you', 'kloor_vestigels_complete');
            check(qDone('the_three_vestigels'), "quest 'the_three_vestigels' complete");
            await pick('tell_me', 'kloor_bishop_reveal');
            await pick('the_dream_games', 'kloor_dream_games');
            await pick('thank_you_for_the_information', null);
            const sp = spores(), m = money();
            if (sp >= 10) {
                await talk(s.kloor, 'kloor_start', 'Kloor Venn (selling spores)');
                await pick('i_want_to_sell_you_some_spores', 'kloor_buy_spores');
                await pick('sell_10_spores', 'kloor_sell_spores_10');
                await pick('confirm');
                const st = cur().dialogState;
                check(/^kloor_(gray|violet)_oltrac_/.test(st) && spores() === sp - 10 && money() > m, `sold 10 spores (${st}: ${m} -> ${money()} dinar)`);
                await closeDlg();
            } else warn(`only ${sp} spores left: no sale`);
        });

        await step('trip:swings', async () => {
            // the dose swings the spores once; entering scenes mid-trip must not swing them again (EffectsSystem, restored)
            const ups = noticesSince(tripStart ?? 0, 'drugs.sporesUp').length + noticesSince(tripStart ?? 0, 'drugs.sporesDown').length;
            const before = notices.slice(0, tripStart ?? 0).filter(n => isNotice(n.text, 'drugs.sporesUp') || isNotice(n.text, 'drugs.sporesDown')).length;
            check(before === 1 && ups === 0, `the Violet dose swung the spores once (${before} at the dose, ${ups} more on the ${notices.slice(tripStart ?? 0).length} notices since)`);
        });

        await step('lift+elphi:anomaly', async () => {
            await go('CrossroadScene');
            await go('ScraperScene');
            let s = await go('ScraperInteriorScene');
            await talk(s.elevator, 'lift_mother_start', 'the Lift-Mother');
            await pick('i_need_to_reach_dr_elphis_floor', 'lift_mother_elphi_floor');
            await pickOr('i_know_the_bishops_secret_its_important_to_reach_d', 'confession_path');
            await pick('thank_you', 'unlock_floor');
            await pick('thank_you', 'goto_elphi_floor');
            await pick('step_out');
            await until(() => game.scene.isActive('ScraperAmbraScene') && cur()?.scene.key === 'ScraperAmbraScene', 20 * 60, 'the lift ride');
            s = await arrive('ScraperAmbraScene');
            const elphi = findObj(s, o => o.type === 'Container' && o.input?.enabled && Math.abs(o.x - (s.drElphi?.x ?? -1)) < 2);
            await talk(elphi, 'dr_elphi_start', 'Dr. Elphi');
            await pick('what_are_you_working_on_now', 'dr_elphi_work_skyship');
            await pick('a_giant_hen', 'dr_elphi_work_captain');
            await pick('and_the_interiors', 'dr_elphi_work_mox');
            await pick('good_luck_with_the_hen', 'dr_elphi_start');
            await pick('i_was_sent_to_investigate_an_anomaly_might_be_conn', 'dr_elphi_anomaly_path');
            await pick('the_bishop_came_here_to_play', 'dr_elphi_bishop_path');
            await pick('whats_in_the_backyard', 'dr_elphi_backyard_info');
            await pick('is_it_dangerous', 'dr_elphi_backyard_danger');
            await pick('ill_be_careful', 'dr_elphi_exit');
            check(hasItem('scraper_backyard_key'), 'backyard key in the bag');
            await pick('thanks_for_the_information', null);
            await talk(elphi, 'dr_elphi_start', 'Dr. Elphi again');
            const keys = rawOptions(s, 'dr_elphi_start').map(o => o.key);
            check(!keys.includes('im_looking_for_someone_the_bishop'), 'her first-visit openers are gone after the key', keys.join(', '));
            await closeDlg();
        });

        await busEnding();
    }

    // ================================================================== branch: the skyship either/or
    async function skyshipBranch() {
        await step('corpse:spores', async () => {
            const s = cur();
            const sp = spores();
            await talk(s.corpse, 'corpseMain', 'the corpse');
            await pick('plant_spores_in_it', 'plantSpores');
            await pick('continue', null);
            check(spores() === sp - 10, `planting costs 10 spores (${sp} -> ${spores()})`);
            check(hasJ('crossroad_corpse_spores_planted') && game.registry.get('crossroadGrowth') === true, 'the corpse grows into a tree (journal + registry)');
            await wait(1);
            check(!!s.skyshipTransition?.input?.enabled, 'the tree is clickable (way up to the skyship)');
            await still('tree');
            await talk(s.corpse, 'corpseExhausted', 'the corpse again');
            check(!rawOptions(s, 'corpseExhausted').some(o => /accept/.test(o.key)), 'no Thorne-Still any more (by design)');
            await closeDlg();
        });

        await step('lift-mother:first', async () => {
            await go('ScraperScene');
            const s = await go('ScraperInteriorScene');
            await talk(s.elevator, 'lift_mother_start', 'the Lift-Mother');
            const keys = rawOptions(s, 'lift_mother_start').map(o => o.key);
            check(!keys.includes('i_need_to_reach_dr_elphis_floor'), "no way to ask for Dr. Elphi's floor before any Bishop story", keys.join(', '));
            await pick('tell_me_about_this_building', 'lift_mother_building');
            await pick('ask_about_something_else', 'lift_mother_start');
            await closeDlg();
            check(hasJ('lift_mother_meeting'), 'journal: the Lift-Mother');
        });

        await step('kloor:violet', async () => {
            await go('ScraperScene');
            await go('CrossroadScene');
            let s = await go('VoxMarket');
            await talk(s.kloor, 'kloor_start', 'Kloor Venn');
            await pick('what_are_you_selling', 'kloor_selling');
            await pick('show_me_what_you_have');
            await wait(0.8);
            s = cur();
            check(!!s.shopSystem?.isOpen && !!paperOpen(), "Kloor's shop opens (on screen)");
            auditScreen();
            await still('kloor_shop');
            await shopBuy('violetOltrac');
            s.shopSystem?.close();
            await wait(1.5);
            if (s.dialogVisible) await closeDlg();
        });

        await step('skyship', async () => {
            const s = await go('CrossroadScene');
            check(!!s.skyshipTransition, 'the tree is there on return');
            const tgt = game.scene.getScene('SkyshipBoardScene');
            let created = false;
            tgt.events.once('create', () => { created = true; });
            await clickObj(s.skyshipTransition, 'the mycelium tree');
            await wait(2);
            auditScreen();
            await still('skyship_lookup');
            try { await until(() => created && game.scene.isActive('SkyshipBoardScene'), 60 * 60, 'the skyship'); pass('Crossroad tree -> SkyshipBoardScene'); }
            catch (e) { fail('the tree did not lead to the skyship in 60 s'); await rescueEnter('SkyshipBoardScene'); return; }
            await arrive('SkyshipBoardScene');
        });

        await step('ulvarex', async () => {
            const s = cur();
            useFromBag('violetOltrac');
            await wait(0.5);
            check(game.registry.get('activeDrugEffect')?.id === 'violetOltrac', 'the Violet Oltrac trip is on');
            try { await until(() => cur().dialogVisible && cur().dialogState === 'ulvarex_notice', 25 * 60, 'Ulvarex'); pass('Ulvarex shows in the puddle and speaks up'); }
            catch (e) { fail(`Ulvarex did not speak up on the skyship deck in 25 s (shown=${s._ulvarex?.shown})`); await force('ulvarex_notice'); }
            await still('ulvarex');
            await pick('ulvarex_crouch', 'ulvarex_reach');
            check(hasJ('met_ulvarex'), 'journal: Ulvarex');
            await pick('ulvarex_what_are_you', 'ulvarex_what');
            await pick('ulvarex_what_bond', 'ulvarex_bond');
            await pick('ulvarex_bond_yes', 'ulvarex_accept');
            check(symbionts()?.hasSymbiont('ulvarex-borrowed-horizon'), 'Ulvarex bonded');
            check(hasJ('symbiont_ulvarex_accepted'), 'journal: Ulvarex accepted');
            await pick('ulvarex_welcome', null);
            await wait(2);
        });

        await step('liris', async () => {
            const s = cur();
            await talk(s.captainLiris, 'captainMain', 'Captain Liris');
            check(hasJ('captain_liris_meeting'), 'journal: Liris');
            await pick('i_need_help_with_an_elevator_system', 'captainElevator');
            await pick('the_floor_counter_is_broken', 'captainFloorCounter');
            await pick('how_does_it_work', 'captainToolExplanation');
            await pick('could_i_borrow_this_tool', 'captainGivesTool');
            check(game.registry.get('fixed_floor_counter') === true && hasJ('floor_counter_tool'), "Liris's calibration tool (registry + journal)");
            await still('liris');
            await pick('thank_you', null);
        });

        await step('gnur:quest', async () => {
            await go('CrossroadScene');
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur');
            await pick('im_looking_for_the_bishop_have_you_seen_her', 'bishop');
            await pick('what_do_you_want', 'rustReclamation');
            await pick('ok_tell_me_more', 'recoverTech');
            check(!!quest('rust_reclamation'), "quest 'rust_reclamation' started");
            await closeDlg();
        });

        await step('clerk:expose', async () => {
            await go('Shed521FloorsScene');
            const s = await go('ShedApplicationsScene');
            await talk(s.clerk, 'start', 'the Applications clerk');
            await pick('what_do_you_know_about_the_living_core', 'living_core_inquiry');
            await pick('gnur_asked_me_to_retrieve_it', 'expose_gnur');
            check(hasUpd('rust_reclamation', 'core_shed_energy'), 'rust_reclamation: core_shed_energy');
            await pick('i_promise_to_leave_it_alone', 'promise_made');
            await pick('he_promised_me_a_to_tell_where_to_find_the_bishop', 'bishop_location');
            check(hasUpd('find_bishop', 'clerk_records_hint'), 'find_bishop: clerk_records_hint');
            await pick('back_to_other_topics', 'start');
            await closeDlg();
        });

        await step('gnur:refuse', async () => {
            await go('Shed521FloorsScene');
            const s = await go('Shed521Scene');
            await talk(s.gnur, 'start', 'Gnur (waiting for the core)');
            await pick('about_that_living_core_you_lied_to_me', 'confront_about_lie');
            await pick('the_clerk_told_me_its_crucial_for_the_sheds_energy', 'refuse_quest');
            check(qDone('rust_reclamation') && hasUpd('rust_reclamation', 'quest_refused'), 'rust_reclamation ended: refused');
            await pick('leave', null);
        });

        await step('clerk:records', async () => {
            await go('Shed521FloorsScene');
            const s = await go('ShedApplicationsScene');
            await talk(s.clerk, 'start', 'the Applications clerk (after the refusal)');
            await pick('gnur_wont_get_the_core', 'core_refused_thanks');
            check(hasUpd('find_bishop', 'bishop_elphi_clerk'), "find_bishop: the Tribunal's records (bishop_elphi_clerk)");
            await still('clerk_records');
            await pick('thank_you_that_helps', 'start');
            await closeDlg();
        });

        await step('lift-mother:tool', async () => {
            await go('Shed521FloorsScene');
            await go('Shed521Scene');
            await go('CrossroadScene');
            await go('ScraperScene');
            const s = await go('ScraperInteriorScene');
            await talk(s.elevator, 'lift_mother_start', 'the Lift-Mother');
            await pick('i_need_to_reach_dr_elphis_floor', 'lift_mother_elphi_floor');
            check(!!quest('level_177_access'), "quest 'level_177_access' started");
            check(hasUpd('level_177_access', 'liris_tool_hint'), 'level_177_access: liris_tool_hint');
            await pick('tribunal_records_permit', 'permit_not_yours');
            check(hasUpd('level_177_access', 'hint_importance') || quest('level_177_access')?.updates?.some(u => /^hint_importance/.test(u.key)), 'level_177_access: the "two stories" hint');
            await pick('ill_find_a_second_one', 'lift_mother_start');
            await pick('i_need_to_reach_dr_elphis_floor', 'lift_mother_elphi_floor');
            await pickOr('ive_a_tool_to_repair_your_floor_counter_perhaps_yo', 'repair_path');
            await pick('thank_you', 'unlock_floor');
            await pick('thank_you', 'goto_elphi_floor');
            await pick('step_out');
            await until(() => game.scene.isActive('ScraperAmbraScene') && cur()?.scene.key === 'ScraperAmbraScene', 20 * 60, 'the lift ride');
            await arrive('ScraperAmbraScene');
            check(qDone('level_177_access'), "quest 'level_177_access' complete");
        });

        await step('elphi:brief', async () => {
            const s = cur();
            const elphi = findObj(s, o => o.type === 'Container' && o.input?.enabled && Math.abs(o.x - (s.drElphi?.x ?? -1)) < 2);
            await talk(elphi, 'dr_elphi_start', 'Dr. Elphi');
            await pick('i_heard_you_design_dreambased_games', 'dr_elphi_games_path');
            await pick('never_mind', 'dr_elphi_exit_brief');
            check(hasItem('scraper_backyard_key'), 'backyard key in the bag');
            check(hasUpd('find_bishop', 'check_shard_backyard'), 'find_bishop: check_shard_backyard');
            await pick('thanks_brief', null);
        });

        await busEnding();
    }

    // ================================================================== the end: the bus, the credits, the end card
    async function busEnding() {
        await step('bus', async () => {
            await go('ScraperInteriorScene');
            await go('ScraperBackyardScene');
            check(hasJ('scraper_backyard'), 'journal: the backyard');
            await go('AbandonedBusScene');
            try { await until(() => cur().dialogVisible && cur().dialogState === 'bishop_found_1', 15 * 60, 'the monologue'); pass('the apprentice walks up to the Bishop, the monologue starts'); }
            catch (e) { fail('the monologue did not start in 15 s'); await force('bishop_found_1'); }
            check(qDone('find_bishop') && hasUpd('find_bishop', 'found_dead_in_bus'), "quest 'find_bishop' complete (found_dead_in_bus)");
            check(hasJ('found_dead_bishop'), 'journal: the Bishop found');
            await still('bus_monologue');
            await pick('bus_mono_next', 'bishop_found_2');
            await pick('bus_mono_next', 'bishop_found_3');
            await pick('bus_mono_next', 'bishop_found_4');
            await pick('bus_mono_end', null);
            try { await until(() => game.scene.isActive('CreditsScene'), 10 * 60, 'the credits'); pass('the credits roll'); }
            catch (e) { fail('no credits after the monologue'); }
            check(game.scene.isPaused('AbandonedBusScene'), 'the bus is paused under the credits');
            await wait(3);
            auditScreen();
            await still('credits');
            await domClick(530, 300);   // skip
            try { await until(() => game.scene.isActive('DemoEndScene'), 40 * 60, 'the end card'); pass('the end card'); }
            catch (e) { fail('no end card after the credits'); return; }
            await wait(2.5);
            auditScreen();
            await still('end_card');
            check(flags().includes('demo_end_bus'), 'onceFlags: demo_end_bus');
        });

        await step('keep-exploring', async () => {
            const end = game.scene.getScene('DemoEndScene');
            const want = L.t('ui.demo.end.continue');
            const txt = findObj(end, o => o.type === 'Text' && o.text === want);
            check(!!txt, `"${want}" on the end card`);
            if (txt) { const b = txt.getBounds(); await domClick(b.centerX, b.centerY); }
            try { await until(() => !game.scene.isActive('DemoEndScene') && game.scene.isActive('AbandonedBusScene'), 6 * 60, 'resume'); pass(`"${want}" resumes the game`); }
            catch (e) { fail(`"${want}" (a click on it) did not close the end card`); rescue('DemoEndScene.close()'); end.close(); await wait(1.5); }
            const s = cur();
            check(s?.scene.key === 'AbandonedBusScene' && !game.scene.isPaused('AbandonedBusScene'), 'back in the bus, running');
            await wait(1);
            check(!s.cutscene, 'the cutscene lock is released');
            await still('after_end');
            await go('ScraperBackyardScene');
            await go('AbandonedBusScene');
            await wait(4);
            check(!cur().dialogVisible && !game.scene.isActive('CreditsScene'), 'a second visit to the bus: no monologue, no credits again');
            await go('ScraperBackyardScene');
        });
    }

    // ================================================================== translation audit of the state (Czech)
    await step('audit', async () => {
        const res = (code, key) => L._resolve(L.languages[code] || {}, key);
        const missing = [];
        for (const q of qs()?.getAllQuests?.() || []) {
            for (const k of ['title', 'description']) if (res(LANG, `quests.${q.id}.${k}`) === undefined) missing.push(`quests.${q.id}.${k}`);
            for (const u of q.updates || []) {
                const tk = u.params?.textKey || u.key;
                if (tk && res(LANG, `quests.${q.id}.updates.${tk}`) === undefined) missing.push(`quests.${q.id}.updates.${tk}`);
            }
        }
        const js = journal();
        for (const e of js?.getAllEntries?.() || [...(js?.entries?.values?.() || [])]) {
            if (e.id === 'edgar_book_completed') continue;   // runtime-built, written in the language of the moment
            for (const k of ['title', 'description']) if (res(LANG, `journal.${e.id}.${k}`) === undefined) missing.push(`journal.${e.id}.${k}`);
            for (const f of js.getFacts(e.id)) if (res(LANG, `journal.${e.id}.facts.${f.id}`) === undefined) missing.push(`journal.${e.id}.facts.${f.id}`);
        }
        for (const it of inv()) if (res(LANG, `items.${it.id}.name`) === undefined) missing.push(`items.${it.id}.name`);
        // quest notices (new / updated / completed / the spores reward) must show where the player is (questSystem.setScene)
        const qn = notices.filter(n => questNoticeKeys.some(k => isNotice(n.text, k)));
        const wrong = qn.filter(n => n.scene !== n.current);
        check(qn.length > 0 && !wrong.length, `all ${qn.length} quest notices showed in the scene the player was in`,
            wrong.map(n => `"${n.text}" shown by ${n.scene} while in ${n.current} [${n.beat}]`).join('; '));
        // Ortolan's five gifts (one per form; a run reaches one): a name in both languages and an icon
        for (const form of ['artisan-exemption-form', 'deformity-form', 'special-dispensation', 'temporary-permit', 'forged-arms-permission']) {
            const gift = armsReward(form);
            if (!gift) { fail(`Ortolan: no gift for ${form}`); continue; }
            for (const code of ['en', 'cs']) if (res(code, `items.${gift.id}.name`) === undefined) missing.push(`(${code}) items.${gift.id}.name`);
            if (!game.textures.exists(gift.icon || gift.id)) fail(`Ortolan's gift ${gift.id}: no icon texture '${gift.icon || gift.id}'`);
        }
        if (missing.length) {
            (CS ? fail : warn)(`${missing.length} quest/journal/item keys missing in lang/${LANG} (the stored English shows): ${missing.join(', ')}`);
        } else pass(`all quest/journal/item texts of this run exist in lang/${LANG}`);
        log(`state: money=${money()} spores=${spores()} G/D=${game.registry.get('growthDecaySystem')?.getGrowth?.()}/${game.registry.get('growthDecaySystem')?.getDecay?.()}`
            + ` symbionts=${[...(symbionts()?.symbionts?.keys?.() || [])].join(',')} bag=${inv().map(i => i.id).join(',')}`);
        log('quests: ' + (qs()?.getAllQuests?.() || []).map(q => `${q.id}${q.isComplete ? '(done)' : ''}`).join(', '));
    });

    // ================================================================== summary
    beat = 'summary';
    const fails = results.filter(r => !r.ok);
    await cap.json(`pt_${tag}_transcript`, { lang: LANG, branch: BRANCH, results, warns, rescues, console: consoleLog,
        i18n: [...issues.values()], tMisses: [...tMisses.values()], transcript });
    log('================ SUMMARY ================');
    log(`lang=${LANG} branch=${BRANCH}: ${results.length - fails.length} passed, ${fails.length} failed, ${warns.length} warnings, ${rescues.length} rescues`);
    fails.forEach(f => log(`  FAILED [${f.beat}] ${f.msg}`));
    const errs = consoleLog.filter(c => c.lvl !== 'warn');
    log(`console errors: ${errs.length}, warnings: ${consoleLog.length - errs.length}`);
    const seen = new Set();
    for (const c of consoleLog) {
        const k = c.lvl + c.msg.slice(0, 120);
        if (seen.has(k)) continue;
        seen.add(k);
        log(`  ${c.lvl} [${c.beat}] ${c.msg.replace(/\n/g, ' | ').slice(0, 300)}`);
    }
    log(`i18n issues on screen: ${issues.size}`);
    const miss = [...tMisses.values()];
    log(`lang keys missing in ${LANG}: ${miss.length}`);
    for (const m of miss) log(`  ${m.kind} ${m.key} [${m.beat} @ ${m.scene}]`);
}
