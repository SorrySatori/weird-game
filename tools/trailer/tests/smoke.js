// Demo smoke test: every demo scene entered, every dialog state shown and every reply clicked (in both dialog
// styles), every clickable thing clicked, every exit walked through, the HUD panels opened in both panel sets, a
// quicksave + quickload. Collects errors and suspicious texts (undefined, raw keys, English in the Czech game).
//   ./tools/trailer/capture.sh --test smoke [--lang cs] [--only SceneKey,SceneKey]
// Report: tools/trailer/out/stills/smoke_<lang>.json, a summary in the terminal ([page] lines).
import { SURVEY_SCENES } from '../shots.js';
import LanguageSystem from '../../../systems/LanguageSystem.js';
import { setSetting } from '../../../systems/GameSettings.js';

const OVERLAYS = new Set(['CreditsScene', 'DemoEndScene', 'PauseMenuScene', 'TransitionScene', 'LoadingScene', 'TrailerCursorScene']);
const NOISE = [/AnimationManager key already exists/, /Texture key already in use/];
const STOP = new Set(['the', 'and', 'you', 'is', 'are', 'of', 'it', 'this', 'that', 'what', 'with', 'your', 'not', 'have', 'was', 'for', "i'm", "it's", "don't", 'he', 'she', 'they', 'will', 'can']);

export default async function smoke({ game, cap, enter, wait, frame, readPixels }) {
    const FPS = cap.args.fps;
    const L = LanguageSystem.getInstance();
    const lang = L.getLanguage();
    const cs = lang !== 'en';

    // --- errors: console.error, uncaught errors, rejections; attributed to whatever runs at the time ---
    let bucket = null;
    const fmt = (a) => a.map(x => (x?.stack || x?.message || (typeof x === 'string' ? x : JSON.stringify(x)))).join(' ').slice(0, 600);
    const origError = console.error.bind(console);
    console.error = (...a) => { const m = fmt(a); if (bucket && !NOISE.some(r => r.test(m))) bucket.push(m); origError(...a); };
    window.addEventListener('error', e => bucket?.push(`uncaught: ${e.message} @ ${e.filename}:${e.lineno}`));
    window.addEventListener('unhandledrejection', e => bucket?.push(`rejection: ${e.reason?.stack || e.reason}`));
    const run = async (fn) => {
        const prev = bucket, mine = [];
        bucket = mine;
        try { await fn(); } catch (e) { mine.push(`threw: ${e?.stack || e}`.slice(0, 600)); }
        bucket = prev;
        return mine;
    };

    // --- text checks ---
    const looksEnglish = (t) => {
        const w = String(t).toLowerCase().match(/[a-z']+/g) || [];
        const n = w.filter(x => STOP.has(x)).length;
        return n >= 2 && n / Math.max(1, w.length) > 0.12 && !/[ěščřžýáíéůúňťďó]/i.test(t);
    };
    const looksCzech = (t) => (String(t).match(/[ěščřžůňťď]/gi) || []).length >= 2;
    const check = (t) => {
        const s = String(t ?? '');
        const out = [];
        if (/\bundefined\b|\bNaN\b|\[object /.test(s)) out.push('undefined/NaN/[object]');
        if (/\{\w+\}/.test(s)) out.push('unfilled {placeholder}');
        if (/\\n/.test(s)) out.push('a literal \\n');
        if (/^(ui|items|quests|journal|factions|locations|exits|symbionts|shop|notifications)\.[\w.]+$/.test(s.trim())) out.push('raw key');
        if (cs && looksEnglish(s)) out.push('English in the Czech game');
        if (!cs && looksCzech(s)) out.push('Czech in the English game');
        return out;
    };

    // --- scene helpers ---
    const sm = game.scene;
    const mainKey = () => sm.scenes.find(s => !OVERLAYS.has(s.scene.key) && [Phaser.Scenes.RUNNING, Phaser.Scenes.PAUSED].includes(s.sys.settings.status))?.scene.key;
    const closeAll = (sc) => {
        try { if (sc.dialogVisible) sc.hideDialog(); } catch (e) { bucket?.push(`hideDialog threw: ${e}`); }
        sc.inventorySystem?.inventoryVisible && sc.inventorySystem.close?.();
        sc.journalUI?.visible && sc.journalUI.close?.();
        sc.questLog?.questPanel?.visible && sc.questLog.close?.();
        sc.mapUI?.visible && sc.mapUI.hide?.();
        sc.gameMenu?.visible && sc.gameMenu.hideMenu?.();
        sc.shopSystem?.isOpen && sc.shopSystem.close?.();
    };
    const settle = async (key) => {
        for (let i = 0; i < 4; i++) {
            for (const o of OVERLAYS) if (o !== 'LoadingScene' && (sm.isActive(o) || sm.isPaused(o))) sm.stop(o);
            if (sm.isPaused(key)) sm.resume(key);
            const sc = sm.getScene(key);
            if (sc?.sys.settings.status === Phaser.Scenes.RUNNING) closeAll(sc);
            await wait(0.25);
        }
    };
    const fresh = async (key) => { const sc = await enter(key); await wait(1.5); await settle(key); return sm.getScene(key); };
    const interactive = (sc, skip) => {
        const out = [];
        const walk = (list) => list.forEach(o => {
            if (o.input?.enabled && o.visible !== false && o.alpha !== 0 && !skip.has(o)) out.push(o);
            if (o.list) walk(o.list);
        });
        walk(sc.children.list);
        return out;
    };
    const label0 = (o) => o.name || o.destinationName || o.texture?.key || (o.text ? `text:${String(o.text).slice(0, 24)}` : o.type);
    const labels = (objs) => { const seen = {}; return objs.map(o => { const l = label0(o); seen[l] = (seen[l] || 0) + 1; return `${l}#${seen[l]}`; }); };
    const press = (sc, o) => {
        const m = o.getWorldTransformMatrix?.();
        const p = sc.input.activePointer;
        const x = m ? m.tx : o.x, y = m ? m.ty : o.y;
        p.x = p.worldX = p.downX = x; p.y = p.worldY = p.downY = y; p.position?.set?.(x, y);
        const ev = { stopPropagation() {}, preventDefault() {} };
        o.emit('pointerover', p, 0, 0, ev);
        o.emit('pointerdown', p, 0, 0, ev);
        o.emit('pointerup', p, 0, 0, ev);
        o.emit('pointerout', p, ev);
    };

    const report = { lang, scenes: {}, panels: {}, save: {}, notifications: [] };
    // every notification's text is checked too (a raw key slipped through one)
    const GS = window.GameScene?.prototype;
    if (GS?.showNotification) {
        const show = GS.showNotification;
        GS.showNotification = function (m, ...rest) {
            // (a symbiont's remark comes in English and is translated when it is drawn: check what is drawn)
            const said = /^([\w-]+): (.*)$/s.exec(String(m));
            const issues = check(said ? `${said[1]}: ${L.symbiontLine(said[2])}` : m);
            if (issues.length) report.notifications.push(`${this.scene.key}: ${issues.join(', ')}: "${String(m).slice(0, 90)}"`);
            return show.call(this, m, ...rest);
        };
    }
    const scenes = cap.args.only || SURVEY_SCENES;

    for (const key of scenes) {
        const R = report.scenes[key] = { misc: [], enter: [], autoDialog: null, dialogs: { states: 0, options: 0, errors: [], brokenNext: [], texts: [], untranslated: [] }, clicks: [], exits: [] };
        cap.log(`smoke ${key}`);
        bucket = R.misc;           // (errors outside a check: re-entering the scene, settling)
        R.enter = await run(async () => { await enter(key); await wait(key === 'IntroScene' ? 12 : 3); });
        let sc = sm.getScene(key);
        if (sc.dialogVisible) R.autoDialog = sc.dialogState || '(object)';
        await settle(key);
        if (key === 'IntroScene' || typeof sc.showDialog !== 'function') continue;

        // --- dialogs: every state shown, every reply clicked, in both styles ---
        const content = sc.dialogContent || {};
        const csDialogs = L.languages?.[lang]?.dialogs?.[key];
        for (const style of ['bubbles', 'cinema']) {
            setSetting('dialogStyle', style);
            for (const state of Object.keys(content)) {
                if (state === 'closeDialog') continue;
                const c = content[state];
                if (!c || typeof c !== 'object') continue;
                if (style === 'bubbles') {
                    R.dialogs.states++;
                    // replies that lead nowhere
                    if (Array.isArray(c.options)) for (const o of c.options) {
                        // (next '' with an onTrigger(option): the trigger picks the next state)
                        const picked = o.next === '' && c.onTrigger?.length > 0;
                        if (typeof o.next === 'string' && !picked && !(o.next in content)) R.dialogs.brokenNext.push(`${state} → ${o.next} (${o.key || o.text})`);
                    }
                    // Czech: a state / reply with no translation whose English shows through
                    if (cs) {
                        const tr = csDialogs?.[state];
                        if (typeof c.text === 'string' && c.text && looksEnglish(c.text)) {
                            const has = tr?.text && (typeof tr.text === 'string' || tr.text[c.textKey || c.text]);
                            if (!has) R.dialogs.untranslated.push(`${state}: text "${c.text.slice(0, 70)}"`);
                        }
                        if (Array.isArray(c.options)) for (const o of c.options) {
                            if (o.text && looksEnglish(o.text) && !tr?.options?.[o.key || o.text]) R.dialogs.untranslated.push(`${state}: reply "${String(o.text).slice(0, 50)}"`);
                        }
                    }
                }
                // shown
                let model = null;
                const errs = await run(async () => {
                    sc = sm.getScene(key);
                    sc.showDialog(state);
                    model = sc.dialogVisible ? sc._dialogModel : null;
                });
                if (errs.length) R.dialogs.errors.push({ state, style, at: 'show', errs });
                if (model && style === 'bubbles') {
                    for (const t of [model.text, ...model.options.map(o => o.label)]) {
                        const issues = check(t);
                        if (issues.length) R.dialogs.texts.push(`${state}: ${issues.join(', ')}: "${String(t).slice(0, 90)}"`);
                    }
                }
                // every reply
                const n = model ? model.options.length : 0;
                for (let i = 0; i < n; i++) {
                    if (style === 'bubbles') R.dialogs.options++;
                    let left = null;
                    const errs2 = await run(async () => {
                        sc = sm.getScene(key);
                        if (sc.sys.settings.status !== Phaser.Scenes.RUNNING) return;
                        sc.showDialog(state);
                        const m = sc._dialogModel;
                        if (!sc.dialogVisible || !m?.options[i]) return;
                        m.options[i].activate();
                        await frame(false);
                        const now = mainKey();
                        if (now !== key) left = now;
                    });
                    if (errs2.length) R.dialogs.errors.push({ state, style, option: i, errs: errs2 });
                    if (left || sm.getScene(key).sys.settings.status !== Phaser.Scenes.RUNNING || [...OVERLAYS].some(o => o !== 'LoadingScene' && sm.isActive(o))) {
                        await fresh(key);
                    }
                }
                sc = sm.getScene(key);
                if (sc.sys.settings.status === Phaser.Scenes.RUNNING) closeAll(sc);
            }
        }
        setSetting('dialogStyle', 'bubbles');

        // --- clicks: everything clickable that isn't an exit ---
        sc = await fresh(key);
        const exits = (sc.transitionManager?.transitionElements || []).map(e => e.zone).filter(Boolean);
        const exitSet = new Set(exits);
        const targets = labels(interactive(sc, exitSet));
        for (let i = 0; i < targets.length; i++) {
            let result = '';
            const errs = await run(async () => {
                sc = sm.getScene(key);
                const objs = interactive(sc, new Set((sc.transitionManager?.transitionElements || []).map(e => e.zone)));
                const o = objs[labels(objs).indexOf(targets[i])];
                if (!o) { result = 'gone'; return; }
                press(sc, o);
                await wait(2.5);
                const now = mainKey();
                result = now !== key ? `→ ${now}` : sc.dialogVisible ? `dialog ${sc.dialogState || ''}` : sc.isModalOpen?.() ? 'panel' : 'ok';
            });
            R.clicks.push({ target: targets[i], result, errs });
            if (mainKey() !== key || [...OVERLAYS].some(o => o !== 'LoadingScene' && sm.isActive(o))) await fresh(key);
            else await settle(key);
        }

        // --- exits: each walked through, the next place must come up clean ---
        for (let i = 0; i < exits.length; i++) {
            let to = null, name = '';
            const errs = await run(async () => {
                sc = await fresh(key);
                const zone = (sc.transitionManager?.transitionElements || [])[i]?.zone;
                if (!zone) { to = 'gone'; return; }
                name = zone.destinationName || '';
                press(sc, zone);
                // (between the two scenes none runs: wait for the next one to be up)
                for (let f = 0; f < 10 * FPS && (mainKey() === key || !mainKey()); f++) await frame(false);
                to = mainKey() === key ? (sc.isTransitioning ? 'stuck transitioning' : 'stayed (closed?)') : (mainKey() || 'none running');
                if (mainKey() !== key) await wait(2.5);
            });
            R.exits.push({ exit: name, to, errs });
        }
        bucket = null;
        const bad = R.misc.length + R.enter.length + R.dialogs.errors.length + R.dialogs.brokenNext.length + R.clicks.filter(c => c.errs.length).length + R.exits.filter(e => e.errs.length).length;
        cap.log(`  ${key}: ${R.dialogs.states} states, ${R.dialogs.options} replies, ${R.clicks.length} clicks, ${R.exits.length} exits; problems ${bad}, texts ${R.dialogs.texts.length}, untranslated ${R.dialogs.untranslated.length}`);
    }

    // --- HUD panels in both sets, the pause menu, the hint lantern ---
    if (!cap.args.only) {
        for (const set of ['apprentice', 'office']) {
            setSetting('panelSet', set);
            const P = report.panels[set] = {};
            const sc = await fresh('CrossroadScene');
            const step = async (name, open, close) => {
                P[name] = await run(async () => { open(); await wait(1); await cap.still(`smoke_${lang}_${set}_${name}`, readPixels(), false); close(); await wait(0.5); });
            };
            await step('inventory', () => sc.inventorySystem.toggleInventory(true), () => sc.inventorySystem.close());
            await step('journal', () => sc.journalUI.toggle(), () => sc.journalUI.close());
            await step('quests', () => sc.questLog.showQuestLog(), () => sc.questLog.hideQuestLog());
            await step('map', () => sc.mapUI.show(), () => sc.mapUI.hide());
            await step('pause', () => sc.gameMenu.showMenu(), () => sc.gameMenu.hideMenu());
            await step('hints', () => sc.showClickableHints(), () => {});
        }
        // --- quicksave in the Crossroads, somewhere else, quickload: back in the Crossroads ---
        report.save = await run(async () => {
            await fresh('CrossroadScene');
            // (held a few frames: a keyup in the same frame clears Phaser's JustDown)
            const key = async (code, keyCode) => {
                window.dispatchEvent(new KeyboardEvent('keydown', { code, key: code, keyCode, bubbles: true }));
                await wait(0.15);
                window.dispatchEvent(new KeyboardEvent('keyup', { code, key: code, keyCode, bubbles: true }));
            };
            await key('F5', 116); await wait(1.5);
            await fresh('VoxMarket');
            await key('F9', 120);
            for (let f = 0; f < 8 * FPS && mainKey() !== 'CrossroadScene'; f++) await frame(false);
            await wait(2);
            if (mainKey() !== 'CrossroadScene') throw new Error(`quickload landed in ${mainKey()}`);
        });
    }

    await cap.json(`smoke_${lang}`, report);
    const total = Object.values(report.scenes).reduce((a, R) => a + R.misc.length + R.enter.length + R.dialogs.errors.length + R.dialogs.brokenNext.length
        + R.clicks.filter(c => c.errs.length).length + R.exits.filter(e => e.errs.length).length, 0);
    cap.log(`smoke ${lang} done: ${total} problems; notifications ${report.notifications.length}; panels ${JSON.stringify(Object.fromEntries(Object.entries(report.panels).map(([k, v]) => [k, Object.values(v).flat().length])))}; save ${report.save.length || 0}`);
}
