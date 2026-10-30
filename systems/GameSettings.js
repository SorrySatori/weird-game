/**
 * Player settings (the Settings panel): music volume, sound volume, fullscreen. Kept in localStorage.
 *
 * Volumes work as two mixer buses behind every sound's own volume, so the scenes' fade-ins, the ampules' music
 * ducking and per-sound volumes keep working untouched: a looping sound (all soundtracks) or the band's set goes
 * through the music bus, everything else through the sound bus. Installed once in main.js (installAudioBuses).
 */
const STORAGE_KEY = 'gameSettings';
const DEFAULTS = { music: 0.8, sfx: 0.9, fullscreen: true };
const MUSIC_KEYS = new Set(['feral-toast']);    // played once, still music

let settings = null;
let manager = null;
const buses = { music: null, sfx: null };

function load() {
    if (settings) return settings;
    settings = { ...DEFAULTS };
    try { Object.assign(settings, JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')); } catch (e) { /* defaults */ }
    return settings;
}

function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)); } catch (e) { /* storage blocked: session only */ }
}

export function getSetting(key) {
    return load()[key];
}

export function setSetting(key, value) {
    load()[key] = value;
    save();
    if (key === 'music' || key === 'sfx') applyBusVolumes();
    if (key === 'fullscreen') applyFullscreen(value);
}

/** the bus a sound plays through; re-created if Phaser rebuilt its master nodes */
function bus(name) {
    if (!manager?.context) return null;
    let b = buses[name];
    if (!b || b.dest !== manager.destination) {
        const gain = manager.context.createGain();
        gain.connect(manager.destination);
        b = buses[name] = { gain, dest: manager.destination };
        applyBusVolumes();
    }
    return b.gain;
}

function applyBusVolumes() {
    const s = load();
    if (buses.music) buses.music.gain.gain.value = s.music;
    if (buses.sfx) buses.sfx.gain.gain.value = s.sfx;
}

/** Route every sound the game creates through the music or the sound bus (Web Audio only). */
export function installAudioBuses(game) {
    const sm = game.sound;
    if (!sm || !sm.context || sm.__busesInstalled) return;
    manager = sm;
    sm.__busesInstalled = true;
    const add = sm.add.bind(sm);
    sm.add = (key, config) => {
        const sound = add(key, config);
        const isMusic = config?.loop === true || MUSIC_KEYS.has(key);
        const out = sound.pannerNode || sound.spatialNode || sound.volumeNode;
        const target = bus(isMusic ? 'music' : 'sfx');
        if (out && target) {
            out.disconnect();
            out.connect(target);
        }
        return sound;
    };
    bus('music'); bus('sfx');
}

/** Electron: the window; a browser: the page */
export function applyFullscreen(on) {
    if (window.appControl?.setFullscreen) {
        window.appControl.setFullscreen(!!on);
        return;
    }
    // a browser wants a user gesture (the toggle's click / key is one); a refusal just leaves the window as it is
    const quiet = () => {};
    if (on && !document.fullscreenElement) document.documentElement.requestFullscreen?.()?.catch(quiet);
    else if (!on && document.fullscreenElement) document.exitFullscreen?.()?.catch(quiet);
}

/** the real state (F11 can change it behind the setting's back) */
export async function isFullscreen() {
    if (window.appControl?.isFullscreen) return !!(await window.appControl.isFullscreen());
    return !!document.fullscreenElement;
}

/** at start: audio buses + a windowed preference (the Electron window opens fullscreen) */
export function initSettings(game) {
    installAudioBuses(game);
    if (load().fullscreen === false && window.appControl?.setFullscreen) window.appControl.setFullscreen(false);
}
