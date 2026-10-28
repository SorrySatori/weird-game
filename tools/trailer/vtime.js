// Virtual clock for frame-exact capture. Loaded before Phaser: performance.now / Date.now / rAF /
// setTimeout / setInterval all run on __vt time, which only advances when the director calls __vt.tick(ms).
// Real I/O (image + XHR loads) still completes asynchronously; the director yields to the event loop between ticks.
(() => {
    const real = {
        setTimeout: window.setTimeout.bind(window),
        clearTimeout: window.clearTimeout.bind(window),
        now: performance.now.bind(performance),
        dateNow: Date.now,
    };
    const dateBase = real.dateNow();
    let now = 0;
    let nextId = 1;
    const timers = new Map(); // id -> { due, fn, args, interval }
    let rafQueue = [];

    performance.now = () => now;
    Date.now = () => dateBase + now;

    window.requestAnimationFrame = (cb) => { const id = nextId++; rafQueue.push({ id, cb }); return id; };
    window.cancelAnimationFrame = (id) => { rafQueue = rafQueue.filter(r => r.id !== id); };

    const addTimer = (fn, ms, args, interval) => {
        const id = nextId++;
        const delay = Math.max(0, Number(ms) || 0);
        timers.set(id, { due: now + delay, fn, args, interval: interval ? Math.max(1, delay) : 0 });
        return id;
    };
    window.setTimeout = (fn, ms, ...args) => addTimer(fn, ms, args, false);
    window.setInterval = (fn, ms, ...args) => addTimer(fn, ms, args, true);
    window.clearTimeout = window.clearInterval = (id) => { timers.delete(id); };

    const runDueTimers = () => {
        // Fire in due order; timers scheduled while firing run in a later pass if already due.
        for (let guard = 0; guard < 10000; guard++) {
            let pick = null;
            for (const [id, t] of timers) if (t.due <= now && (!pick || t.due < pick[1].due)) pick = [id, t];
            if (!pick) return;
            const [id, t] = pick;
            if (t.interval) t.due += t.interval; else timers.delete(id);
            try { typeof t.fn === 'function' ? t.fn(...t.args) : (0, eval)(String(t.fn)); }
            catch (e) { console.error('[vtime] timer error', e); }
        }
    };

    window.__vt = {
        real,
        get now() { return now; },
        // Advance the clock by ms, fire due timers, then run one animation frame.
        tick(ms) {
            now += ms;
            runDueTimers();
            const q = rafQueue;
            rafQueue = [];
            for (const r of q) {
                try { r.cb(now); } catch (e) { console.error('[vtime] rAF error', e); }
            }
        },
        // Let real async work (asset loads, IPC replies) run.
        yieldReal: () => new Promise(res => real.setTimeout(res, 0)),
    };

    // A hidden capture window must still count as visible, or Phaser pauses its loop.
    Object.defineProperty(document, 'hidden', { get: () => false });
    Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });
    document.hasFocus = () => true;
})();
